import json
from services.llm_service import LLMService

class BacklogGenAgent:
    def __init__(self):
        self.llm = LLMService()

    async def generate_backlog(self, trd_content: str, nfr_content: str = "", council_reviews: dict = None, raw_requirements: list = None):
        """
        Derives an enterprise Azure DevOps hierarchy (Epics ➔ Features ➔ User Stories ➔ Tasks)
        ingesting the synthesized Functional Spec (TRD), NFRs, Council Reviews, and complete raw extraction array.
        """
        from services.template_service import TemplateService
        ts = TemplateService()
        skill_prompt = ts.load_skill_prompt("backlog_architect")
        
        from utils.token_optimizer import TokenOptimizer
        compressed_trd = TokenOptimizer.compress_trd_for_backlog(trd_content, max_chars=35000)
        
        import re
        extracted_fr_ids = set(re.findall(r'\[?(FR-\d+)\]?', trd_content))
        if raw_requirements and isinstance(raw_requirements, list):
            for r in raw_requirements:
                if isinstance(r, dict):
                    rid = r.get("id") or r.get("req_id")
                    if rid: extracted_fr_ids.add(str(rid).upper())

        fr_tags = sorted(list(extracted_fr_ids))
        fr_count_mandate = ""
        raw_reqs_section = ""

        if raw_requirements and isinstance(raw_requirements, list) and len(raw_requirements) > 0:
            raw_reqs_section = f"\n\nCOMPLETE EXTRACTED FUNCTIONAL REQUIREMENTS ARRAY ({len(raw_requirements)} Requirements):\n"
            for r in raw_requirements[:120]:
                if isinstance(r, dict):
                    rid = r.get("id") or r.get("req_id") or "FR-xxx"
                    title = r.get("title") or r.get("name") or ""
                    desc = r.get("description") or r.get("text") or ""
                    raw_reqs_section += f"- [{rid}] {title}: {desc}\n"

        if len(fr_tags) >= 15:
            fr_count_mandate = f"""
CRITICAL PROPORTIONAL SCALING MANDATE:
The input document contains {len(fr_tags)} Functional Requirements (including {', '.join(fr_tags[:10])}...).
You MUST architect a large, comprehensive backlog with at least 6 to 12 Epics, 20 to 40 Features, and 40 to 90+ User Stories.
DO NOT COMPRESS EVERYTHING INTO A SINGLE EPIC OR SKIP REQUIREMENTS. Map all {len(fr_tags)} Functional Requirements across multiple domain Epics!
"""
        
        nfr_section = f"\n\nNON-FUNCTIONAL REQUIREMENTS & BUSINESS RULES:\n{nfr_content[:15000]}" if nfr_content else ""
        reviews_section = f"\n\nAGENTIC COUNCIL REVIEWS (Security, UX, QA, Architecture):\n{json.dumps(council_reviews, indent=2)[:15000]}" if council_reviews else ""
        
        prompt = f"""
{skill_prompt}

ENTERPRISE PRODUCTION INSTRUCTION:
Architect a comprehensive, production-grade Azure DevOps hierarchical backlog (Epics ➔ Features ➔ User Stories ➔ Tasks) from the provided inputs below.

STRATEGIC DOMAIN RULES:
1. EPICS GROUPING: Organically group Epics by Functional Domain Sub-Systems (e.g., Auth & Access Control, Core Business Operations, Security & Compliance, Integration & API Gateway, Reporting & Telemetry).
2. USER STORY FORMAT: User Story TITLE must be a CONCISE 3 to 7-word feature title (e.g. "[FR-005] Policy Search & Filter Panel"). The DESCRIPTION field must contain the formal statement "As a [persona], I want to [action], so that [value]" followed by Business Context, Workflow Impact, and Functional Rules. NEVER set the TITLE to the "As a..." sentence!
3. ACCEPTANCE CRITERIA (BDD): Every acceptance criterion MUST follow Behavior-Driven Development Gherkin syntax: "Given [precondition], When [user action], Then [expected system behavior]".
4. TECHNICAL TASKS: Every User Story MUST include specific, actionable engineering tasks (e.g., Frontend Component Task, Backend API/DB Schema Task, QA Automation Spec Task).
5. RELEASE PHASING: Assign MoSCoW priorities (Must, Should, Could, Won't) and Release Phasing (MVP, Phase 2, Phase 3).

{fr_count_mandate}

TRD CONTENT:
{compressed_trd}
{raw_reqs_section}
{nfr_section}
{reviews_section}
"""

        max_retries = 2
        for attempt in range(max_retries):
            print(f" [BacklogArchitect] Structuring backlog from TRD ({len(trd_content)} chars)... (Attempt {attempt+1}/{max_retries})")
            response = await self.llm.call(prompt, provider="azure", agent_name="BacklogArchitect")
            print(f" [BacklogArchitect] LLM response received. Attempting JSON parse...")

            from utils.json_extractor import extract_json_from_llm_response
            parsed = extract_json_from_llm_response(response)

            if isinstance(parsed, dict) and "error" not in parsed:
                parsed = self.sanitize_backlog_json(parsed)
                num_epics = len(parsed.get('epics', []))
                print(f" [BacklogArchitect] SUCCESS: Parsed & sanitized {num_epics} Epics from LLM response.")
                return parsed
            
            print(f" [BacklogArchitect] JSON PARSE ERROR: {parsed.get('error')}")
            if attempt == max_retries - 1:
                return parsed
            continue

    def sanitize_backlog_json(self, parsed_json):
        """
        Sanitizes user story titles and descriptions to prevent duplicate content.
        Ensures story title is a clean, short 3-7 word title (e.g. '[FR-001] User Authentication Panel')
        instead of repeating the full 'As a persona, I want to...' sentence in the title.
        """
        if not isinstance(parsed_json, dict) or "epics" not in parsed_json:
            return parsed_json

        import re
        for epic in parsed_json.get("epics", []):
            if not isinstance(epic, dict): continue
            for feature in epic.get("features", []):
                if not isinstance(feature, dict): continue
                for story in feature.get("user_stories", []):
                    if not isinstance(story, dict): continue
                    
                    title = story.get("title", "")
                    desc = story.get("description", "")
                    req_id = story.get("requirement_id") or ""
                    
                    # Check if title starts with "As a" or "As an"
                    if re.match(r"^As\s+an?\s+", title, re.I):
                        # Extract the action part from "I want to [action] so that"
                        action_match = re.search(r"I\s+want\s+to\s+([^,.]+?)(?:\s+so\s+that|\.|$)", title, re.I)
                        if action_match:
                            clean_action = action_match.group(1).strip()
                            clean_title = clean_action[0].upper() + clean_action[1:]
                        else:
                            clean_title = re.sub(r"^As\s+an?\s+[^,]+,\s*", "", title, flags=re.I)
                            clean_title = clean_title[0].upper() + clean_title[1:] if clean_title else "User Story"
                        
                        if req_id and not clean_title.startswith(f"[{req_id}]") and not clean_title.startswith(req_id):
                            clean_title = f"[{req_id}] {clean_title}"
                            
                        story["title"] = clean_title
                        
                    # Ensure description includes the INVEST statement if missing
                    if desc and not re.search(r"As\s+an?\s+", desc, re.I) and re.match(r"^As\s+an?\s+", title, re.I):
                        story["description"] = f"**User Story Statement:**\n{title}\n\n{desc}"

        return parsed_json

    async def generate_backlog_from_brd(self, raw_brd_text: str):
        """
        Intelligently converts a raw BRD directly into a hierarchical ADO backlog without needing a TRD.
        """
        prompt = f"""
        Analyze the following raw Business Requirements Document (BRD) and architect a comprehensive Azure DevOps hierarchical backlog directly from it.
        The backlog must strictly reflect the functional and technical requirements described in the BRD.
        
        Structure:
        - Epics: High-level business initiatives.
        - Features: Technical capabilities.
        - User Stories: Granular requirements.
        - Tasks: Specific development steps.

        STRATEGIC GUIDELINES:
        1. DISTRIBUTION: Do NOT put everything in MVP. Assign at least 30% of features to Phase 2 or Phase 3.
        2. MOSCOW: Be critical. 'Must' is only for core functionality.
        3. INDUSTRY STANDARDS (INVEST): User stories must follow the INVEST framework (Independent, Negotiable, Valuable, Estimable, Small, Testable).
        4. DESCRIPTION FORMAT: Every user story description MUST strictly follow the format: "As a [persona], I want to [action], so that [value/benefit]."
        5. ACCEPTANCE CRITERIA (BDD): Every acceptance criterion MUST strictly follow the Behavior-Driven Development (BDD) Gherkin syntax: "Given [context], When [action], Then [outcome]."

        Provide the output in the following JSON format:
        {{
          "epics": [
            {{
              "title": "",
              "features": [
                {{
                  "title": "",
                  "user_stories": [
                    {{
                      "title": "",
                      "description": "As a [persona], I want to [action], so that [value].",
                      "acceptance_criteria": [
                        "Given [context], When [action], Then [outcome]",
                        "Given [context], When [action], Then [outcome]"
                      ],
                      "story_points": 5,
                      "priority": "1",
                      "moscow": "Must/Should/Could/Won't",
                      "release_phase": "MVP/Phase 2/Phase 3",
                      "tasks": ["Task A", "Task B"]
                    }}
                  ]
                }}
              ]
            }}
          ]
        }}
        
        Raw BRD Content:
        {raw_brd_text}
        """
        print(f" [DirectBacklogArchitect] Analyzing raw BRD context: {len(raw_brd_text)} chars")
        response = await self.llm.call(prompt, provider="azure", agent_name="DirectBacklogArchitect")
        print(f" [DirectBacklogArchitect] LLM response received. Length: {len(response) if isinstance(response, str) else 'Object'} chars. Attempting JSON parse...")

        try:
            start = response.find("{")
            end = response.rfind("}") + 1
            if start == -1 or end == 0:
                print(" [DirectBacklogArchitect] ERROR: No JSON bounds `{ ... }` found in LLM response.")
                return {"error": "No JSON found in response", "raw": response}
                
            parsed = json.loads(response[start:end])
            num_epics = len(parsed.get('epics', []))
            print(f" [DirectBacklogArchitect] SUCCESS: Successfully parsed {num_epics} Epics from raw BRD.")
            return parsed
        except Exception as e:
            print(f" [DirectBacklogArchitect] JSON PARSE ERROR: {str(e)}")
            print(f"--- RAW LLM RESPONSE PREVIEW (First 500 chars) ---")
            print(response[:500] if isinstance(response, str) else str(response))
            print("--------------------------------------------------")
            return {"error": f"Failed to parse LLM response: {str(e)}", "raw": response}

    async def generate_stories_for_epic(self, epic_data: dict):
        """
        Decomposes an existing ADO Epic or Feature into Features, User Stories, and Tasks.
        """
        prompt = f"""
        Act as a Senior Agile Business Analyst. You have been given an existing Azure DevOps Epic or Feature.
        Your task is to decompose this item into a structured hierarchy of Features (if it's an Epic), User Stories, and Tasks.
        
        Input Item:
        Title: {epic_data.get('title')}
        Type: {epic_data.get('type')}
        Description: {epic_data.get('description', 'No description provided')}
        
        Return the output strictly in the following JSON format:
        {{
            "epics": [
                {{
                    "id": "E-01",
                    "title": "{epic_data.get('title')}",
                    "description": "...",
                    "features": [
                        {{
                            "id": "F-01",
                            "title": "...",
                            "description": "...",
                            "user_stories": [
                                {{
                                    "id": "US-01",
                                    "title": "...",
                                    "description": "...",
                                    "acceptance_criteria": ["..."],
                                    "tasks": [
                                        {{"title": "...", "estimated_hours": 4}}
                                    ]
                                }}
                            ]
                        }}
                    ]
                }}
            ]
        }}
        """
        print(f" [BacklogArchitect] Generating stories for existing {epic_data.get('type')}: {epic_data.get('title')}")
        response = await self.llm.call(prompt, provider="azure", agent_name="BacklogArchitect")
        
        try:
            start = response.find("{")
            end = response.rfind("}") + 1
            return json.loads(response[start:end])
        except Exception as e:
            print(f" Error parsing generated stories: {e}")
            return {"error": "Failed to generate stories from ADO Epic."}
