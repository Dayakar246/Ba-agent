import re
from services.llm_service import LLMService
from services.ado_service import AzureDevOpsService

def _clean_json_output(res_text: str) -> str:
    if not res_text:
        return res_text
    clean = res_text.strip()
    if clean.startswith("```"):
        clean = re.sub(r'^```(?:json)?\n', '', clean, flags=re.IGNORECASE)
        clean = re.sub(r'\n```$', '', clean).strip()
    match = re.search(r'(\[\s*\{[\s\S]*\}\s*\]|\{\s*"test_cases"[\s\S]*\})', clean)
    if match:
        return match.group(1)
    return clean

class TestCaseAgent:
    def __init__(self):
        self.llm = LLMService()
        self.ado_service = AzureDevOpsService()

    async def draft_test_cases(self, backlog_json: str, functional_spec: str = "") -> str:
        """
        Drafts exhaustive, production-ready QA test cases by analyzing BOTH the Functional Specification (TRD)
        and the Backlog User Stories with Acceptance Criteria.
        """
        from services.template_service import TemplateService
        ts = TemplateService()
        skill_prompt = ts.load_skill_prompt("test_case_architect")
        
        from utils.token_optimizer import TokenOptimizer
        compact_backlog = TokenOptimizer.compress_backlog_for_tests(backlog_json, max_chars=30000)
        compressed_spec = TokenOptimizer.compress_trd_for_backlog(functional_spec, max_chars=30000)
        
        spec_section = f"\n\n--- FUNCTIONAL SPECIFICATION (TRD) ---\n{compressed_spec}" if compressed_spec else ""
        backlog_section = f"\n\n--- ENGINEERING BACKLOG (USER STORIES & ACCEPTANCE CRITERIA) ---\n{compact_backlog}" if compact_backlog else ""
        
        context_prompt = f"""
{skill_prompt}

CRITICAL INSTRUCTION: Analyze the provided Functional Specification (TRD) and Engineering Backlog below.
Generate an EXHAUSTIVE, COMPREHENSIVE QA Test Suite (at least 15 to 35 test cases) covering EVERY Epic, Feature, and User Story.

For every User Story and Functional Requirement, generate:
1. Positive Happy Path Test Cases
2. Negative / Validation Error Test Cases
3. Edge Case / Boundary Value Test Cases
4. Integration & Security / Authorization Test Cases
5. Production-Ready Playwright TypeScript (.spec.ts) automation code!

{spec_section}
{backlog_section}

Output MUST strictly follow the JSON schema:
{{
  "test_cases": [
    {{
      "test_case_id": "TC-001",
      "title": "Clear descriptive title",
      "user_story_id": "US-001",
      "type": "Functional/Security/Negative",
      "priority": "High/Medium/Low",
      "preconditions": "Preconditions required",
      "steps": ["Step 1", "Step 2"],
      "expected_result": "Expected outcome",
      "automation_status": "Automated"
    }}
  ],
  "playwright_script": "// Complete Playwright TypeScript Test Script..."
}}
"""
        from utils.json_extractor import extract_json_from_llm_response
        parsed_res = None
        system_instruction = "You are a Lead QA Architect. You output ONLY valid, production-ready JSON matching the requested schema. Never output conversational preamble, markdown triple backticks, or trailing prose."
        
        for attempt in range(1, 3):
            print(f" [TestCaseAgent] Generating comprehensive test suite (Attempt {attempt}/2)...")
            prompt_str = context_prompt if attempt == 1 else context_prompt + "\n\nCRITICAL FIX: Output ONLY pure raw JSON starting with '{' and ending with '}'."
            messages = [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt_str}
            ]
            drafted_tests = await self.llm.call(
                prompt=prompt_str,
                provider="azure",
                agent_name="TestCaseGeneratorDirect",
                messages=messages,
                response_format={"type": "json_object"}
            )
            
            parsed_res = extract_json_from_llm_response(drafted_tests)
            if isinstance(parsed_res, dict) and "error" not in parsed_res:
                return parsed_res

            cleaned_str = _clean_json_output(drafted_tests)
            second_try = extract_json_from_llm_response(cleaned_str)
            if isinstance(second_try, dict) and "error" not in second_try:
                return second_try
            
        return parsed_res

    async def generate_tests_for_workitem(self, item_id: str) -> str:
        """
        Fetches an ADO work item by ID and generates ADO-compatible Test Cases.
        Uses a Critic Loop to ensure high accuracy and no hallucinations.
        """
        # Fetch data
        work_item_data = await self.ado_service.get_work_item(item_id)
        title = work_item_data.get("System.Title", "Unknown Title")
        description = work_item_data.get("System.Description", "No description provided.")
        acceptance_criteria = work_item_data.get("Microsoft.VSTS.Common.AcceptanceCriteria", "No explicit criteria.")

        from services.template_service import TemplateService
        ts = TemplateService()
        skill_prompt = ts.load_skill_prompt("test_case_architect")

        context_prompt = f"""
{skill_prompt}

Generate exhaustive test cases for the following User Story:

STORY TITLE: {title}

STORY DESCRIPTION:
{description}

ACCEPTANCE CRITERIA:
{acceptance_criteria}
"""
        print(f" [TestCaseAgent] Generating drafted tests for: {title}")
        
        # Phase 1: Generation (Fast/Azure)
        drafted_tests = await self.llm.call(
            prompt=context_prompt,
            provider="azure",
            agent_name="TestCaseGenerator"
        )

        # Phase 2: Critic Review (High Accuracy/Azure)
        critic_prompt = f"""
You are a Lead QA Automation Reviewer and Principal Software Engineer in Test. Review the drafted test cases and Playwright script below against the original User Story.

ORIGINAL STORY:
Title: {title}
Description: {description}
Acceptance Criteria: {acceptance_criteria}

DRAFTED TESTS & PLAYWRIGHT SCRIPT:
{drafted_tests}

YOUR STRICT REVIEW RULES:
1. **Zero Hallucinations**: Verify that NO test cases assume functionality not explicitly stated or logically required by the story.
2. **Enterprise QA Metrics**: Ensure every test case includes explicit `priority`, `severity`, `test_technique`, `preconditions`, `test_data`, and step-by-step actions with expected results.
3. **Playwright Script Audit**:
   - Verify the `playwright_script` is production-ready TypeScript code using `@playwright/test`.
   - Ensure it uses resilient user-centric locators (`getByRole`, `getByLabel`, `getByTestId`).
   - Confirm web-first async assertions (`await expect(...).toBeVisible()`).
   - Check that it accurately mirrors the manual test steps defined in `test_cases`.
4. **JSON Output Standard**: Output the FINAL response in a JSON payload strictly adhering to `test_cases_structure.json`. Do NOT include markdown triple backticks around the JSON. Do NOT include any intro preamble.
"""
        print(f" [TestCaseAgent] Critic loop verifying accuracy & Playwright script...")
        
        final_tests = await self.llm.call(
            prompt=critic_prompt,
            provider="azure",
            agent_name="TestCaseReviewer"
        )

        return _clean_json_output(final_tests)

    async def sync_tests_to_ado(self, parent_id: str, markdown_content: str) -> dict:
        """
        Parses the Markdown tests and creates 'Test Case' work items in ADO, linking them to the parent.
        """
        print(f" [TestCaseAgent] Syncing tests to ADO Parent {parent_id}")
        
        # For simplicity in this PoC, we will create a single 'Task' (or 'Test Case' if the process supports it) 
        # containing the full markdown, linked to the parent.
        # In a full enterprise integration, we would parse each table row and create specific Test Steps via the ADO REST API.
        
        title = f"Test Cases for Item {parent_id}"
        description_html = markdown_content.replace("\\n", "<br/>").replace("```markdown", "").replace("```", "")
        
        # Attempt to create a "Test Case". If the ADO project doesn't have Test Case type, it will fail, 
        # but standard Agile/Scrum templates usually do.
        try:
            res = await self.ado_service.create_work_item(
                title=title,
                item_type="Task", # Using Task as a universally supported type for the MVP, could be 'Test Case'
                description=description_html,
                parent_id=int(parent_id),
                tags="AI-Generated, QA"
            )
            return {"status": "success", "item_id": res.get("id")}
        except Exception as e:
            return {"status": "error", "message": str(e)}
