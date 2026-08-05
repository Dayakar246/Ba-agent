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

        if len(fr_tags) <= 10:
            scope_instruction = f"""
DYNAMIC BACKLOG ARCHITECTURE (FOCUSED COMPONENT):
The input document is a focused requirement package containing {len(fr_tags)} requirements ({', '.join(fr_tags[:10])}).
1. DYNAMIC FEATURE CLUSTERING: Cluster requirements by functional sub-system capability into 2 to 4 distinct Features (e.g. "Occupancy Intake Module", "360Value Prefill & Integration Engine"). Group 2 or more related User Stories under each Feature based on domain similarity.
2. NO ARTIFICIAL EPICS: If the scope is a single LOB component workflow, omit the "epics" key completely and output top-level "features" array directly in the JSON.
3. NON-REDUNDANT NAMING: Feature titles represent functional modules, while User Story titles represent specific requirement capabilities (e.g. "[REQ-001] Occupancy Selection Dropdown"). A Feature title and User Story title MUST NEVER be identical.
"""
        elif len(fr_tags) >= 15:
            scope_instruction = f"""
CRITICAL PROPORTIONAL SCALING MANDATE:
The input document contains {len(fr_tags)} Functional Requirements.
Organically group Epics by Functional Domain Sub-Systems. Each Feature must group MULTIPLE related User Stories. Feature title and User Story title MUST NEVER be identical.
"""
        else:
            scope_instruction = """
DYNAMIC BACKLOG ARCHITECTURE:
Infer the appropriate hierarchy from source requirements. Cluster requirements into 2 to 4 Features, grouping multiple User Stories under each Feature. Feature title and User Story title MUST NEVER be identical.
"""

        nfr_section = f"\n\nNON-FUNCTIONAL REQUIREMENTS & BUSINESS RULES:\n{nfr_content[:15000]}" if nfr_content else ""
        reviews_section = f"\n\nAGENTIC COUNCIL REVIEWS (Security, UX, QA, Architecture):\n{json.dumps(council_reviews, indent=2)[:15000]}" if council_reviews else ""
        
        prompt = f"""
{skill_prompt}

ENTERPRISE PRODUCTION INSTRUCTION:
Architect a production-grade Azure DevOps backlog from the provided inputs below.

STRATEGIC DOMAIN RULES:
1. ADAPTIVE HIERARCHY & GROUPING: Cluster requirements into 2 to 4 Features based on functional domain similarity. Feature titles must represent sub-system modules, while User Story titles represent specific requirement capabilities (e.g. "[REQ-001] Occupancy Selection Dropdown"). A Feature title and User Story title MUST NEVER be identical.
2. USER STORY FORMAT: User Story TITLE must be a CONCISE 3 to 7-word feature title with tag (e.g. "[REQ-001] Occupancy Selection Dropdown"). The DESCRIPTION field must contain ONLY the formal statement "As a [persona], I want to [action], so that [value]".
3. ACCEPTANCE CRITERIA (BDD): Every acceptance criterion MUST follow Behavior-Driven Development Gherkin syntax with Given, When, Then on separate lines:
"Given [precondition]
When [user action]
Then [expected system behavior]"
4. TECHNICAL TASKS: Every User Story MUST include specific, actionable engineering tasks.
5. RELEASE PHASING: Assign MoSCoW priorities (Must, Should, Could, Won't) and Release Phasing (MVP, Phase 2, Phase 3).

{scope_instruction}

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
                num_items = len(parsed.get('epics', [])) or len(parsed.get('features', []))
                print(f" [BacklogArchitect] SUCCESS: Parsed & sanitized backlog from LLM response ({num_items} top-level nodes).")
                return parsed
            
            print(f" [BacklogArchitect] JSON PARSE ERROR: {parsed.get('error')}")
            if attempt == max_retries - 1:
                return parsed
            continue

    def sanitize_backlog_json(self, parsed_json: dict) -> dict:
        """
        Sanitizes user story titles and descriptions across adaptive backlog structures.
        Supports both top-level 'epics' and top-level 'features'.
        """
        if not isinstance(parsed_json, dict):
            return parsed_json

        import re
        def sanitize_story(story, feature_title=""):
            if not isinstance(story, dict): return
            title = story.get("title", "")
            desc = story.get("description", "")
            raw_req_id = story.get("requirement_id") or ""
            req_id = raw_req_id.replace("FR-", "REQ-") if "FR-" in raw_req_id else raw_req_id
            story["requirement_id"] = req_id

            # 1. Clean Title if LLM put "As a ..." in title
            if re.match(r"^As\s+an?\s+", title, re.I):
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
            elif req_id and "FR-" in title:
                story["title"] = title.replace("FR-", "REQ-")

            # 2. Extract clean INVEST statement ONLY
            full_text = f"{story.get('title', '')}\n{desc}"
            invest_match = re.search(r"As\s+an?\s+[^,.]+,\s*I\s+want\s+to\s+[^,.]+,\s*so\s+that\s+[^.\n]+", full_text, re.I)
            if invest_match:
                clean_stmt = invest_match.group(0).strip()
                clean_stmt = re.sub(r"^\*\*\s*(?:User Story|Description)[^*]*\*\*:?\s*", "", clean_stmt, flags=re.I).strip()
                story["description"] = clean_stmt

            # 3. Format Acceptance Criteria to have Given, When, Then on separate lines
            acs = story.get("acceptance_criteria", [])
            formatted_acs = []
            for ac in acs:
                if isinstance(ac, str):
                    clean_ac = ac.replace("Given ", "Given ").replace(", When ", "\nWhen ").replace(", Then ", "\nThen ").replace(" When ", "\nWhen ").replace(" Then ", "\nThen ")
                    formatted_acs.append(clean_ac)
                else:
                    formatted_acs.append(ac)
            story["acceptance_criteria"] = formatted_acs

            # 4. Contextualize generic Technical Tasks
            tasks = story.get("tasks", [])
            cleaned_tasks = []
            story_feature_context = story.get("title", "").replace(f"[{req_id}]", "").strip() or feature_title
            for task in tasks:
                task_str = task if isinstance(task, str) else (task.get("title") if isinstance(task, dict) else str(task))
                if re.match(r"^(?:Implement|Handle|Populate|Build|Create|Update)\s*$", task_str, re.I):
                    task_str = f"{task_str} {story_feature_context} component logic"
                elif re.match(r"^(?:Implement|Handle|Populate)\s+(?:backend|frontend|api|database|ui|logic|service)\s*$", task_str, re.I):
                    task_str = f"{task_str} for {story_feature_context}"
                cleaned_tasks.append(task_str)
            story["tasks"] = cleaned_tasks

        def get_story_req_num(story):
            if not isinstance(story, dict): return 999
            req_id = story.get("requirement_id") or story.get("title") or ""
            match = re.search(r"REQ-(\d+)", str(req_id), re.I) or re.search(r"FR-(\d+)", str(req_id), re.I) or re.search(r"\d+", str(req_id))
            if match:
                try:
                    return int(match.group(1)) if match.lastindex and match.lastindex >= 1 else int(match.group(0))
                except Exception:
                    return 999
            return 999

        def get_feature_min_req_num(feature):
            if not isinstance(feature, dict): return 999
            stories = feature.get("user_stories", [])
            if not stories: return 999
            return min([get_story_req_num(s) for s in stories])

        def sanitize_feature(feature):
            if not isinstance(feature, dict): return
            f_title = feature.get("title", "")
            stories = feature.get("user_stories", [])
            for story in stories:
                sanitize_story(story, f_title)
            # Sort stories numerically by requirement ID (REQ-001 -> REQ-002 -> REQ-003)
            stories.sort(key=get_story_req_num)
            feature["user_stories"] = stories

        if "epics" in parsed_json and isinstance(parsed_json["epics"], list):
            for epic in parsed_json.get("epics", []):
                if not isinstance(epic, dict): continue
                features = epic.get("features", [])
                for feature in features:
                    sanitize_feature(feature)
                features.sort(key=get_feature_min_req_num)
                epic["features"] = features
        elif "features" in parsed_json and isinstance(parsed_json["features"], list):
            features = parsed_json.get("features", [])
            for feature in features:
                sanitize_feature(feature)
            features.sort(key=get_feature_min_req_num)
            parsed_json["features"] = features

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
