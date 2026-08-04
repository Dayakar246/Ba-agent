import sys, os
sys.path.append(os.path.abspath('backend'))

from utils.json_extractor import extract_json_from_llm_response

raw = """```json BoxFitassistant<|reserved_special_token_109
{
  "document_summary": "Test Summary",
  "functional_requirements": []
}
```"""

res = extract_json_from_llm_response(raw)
print("PARSED RESULT:", res)
assert res.get("document_summary") == "Test Summary"
print("ALL SPECIAL TOKEN SANITIZATION TESTS PASSED!")
