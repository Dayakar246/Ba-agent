import json
from services.llm_service import LLMService

class ExtractionAgent:
    def __init__(self):
        self.llm = LLMService()

    async def extract_content(self, text: str, context_type: str = "document"):
        """
        Uses AI to extract structured requirements from text with channel-specific context.
        """
        
        channel_guidance = {
            "document": "Focus on formal functional and non-functional specifications from the BRD/PRD.",
            "text": "Formalize the provided notes or text into professional-grade business requirements.",
            "visual": "Analyze the UI description (from Vision Agent) and extract functional interactions and data fields.",
            "meeting": "Identify key stakeholder decisions, agreed-upon features, and action items from the transcript."
        }.get(context_type, "Focus on formal functional specifications.")

        prompt = f"""
        Role: Senior Business Analyst Agent
        Channel: {context_type.upper()}
        Guidance: {channel_guidance}

        Extract structured requirements from the following source material.
        Return the output in the following JSON format:
        {{
          "document_summary": "A concise overview of the source material",
          "quality_score": 0.0, 
          "assessment": {{
            "clarity": "High/Med/Low",
            "completeness": "High/Med/Low",
            "contradictions": [],
            "missing_sections": []
          }},
          "functional_requirements": [{{ 
            "id": "FR-001", 
            "description": "Clear, concise requirement", 
            "priority": "High/Medium/Low",
            "ambiguity_flag": false,
            "clarification_note": ""
          }}],
          "non_functional_requirements": [{{ "id": "NFR-001", "description": "" }}],
          "business_rules": [{{ "id": "BR-001", "description": "" }}],
          "assumptions": [],
          "dependencies": [],
          "open_questions": []
        }}
        
        CRITICAL: Output ONLY a valid JSON object adhering strictly to the schema above. Do NOT include any intro text, preamble (such as 'Here is the JSON...'), or conversational explanations before or after the JSON.
        
        Source Content ({context_type}):
        {text[:120000]}
        """
        
        # We use a robust model for extraction to ensure high fidelity
        response = await self.llm.call(prompt, provider="azure")

        from utils.json_extractor import extract_json_from_llm_response
        return extract_json_from_llm_response(response)
