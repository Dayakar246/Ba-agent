import glob, re

for f in glob.glob('backend/agents/*.py'):
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # We want to safely extract JSON if markdown wrappers are present
    # We will replace all json.loads(response) that aren't already wrapped in start/end logic
    
    def safe_json_replacer(match):
        # If the code already has "response.find('{')", skip replacing
        return """
            if isinstance(response, str):
                start = response.find('{')
                end = response.rfind('}') + 1
                if start != -1 and end != 0:
                    response = json.loads(response[start:end])
                else:
                    response = json.loads(response)
"""
    
    new_content = re.sub(
        r'if isinstance\(response,\s*str\):\s*response\s*=\s*json\.loads\(response\)',
        safe_json_replacer,
        content
    )
    
    if new_content != content:
        with open(f, 'w', encoding='utf-8') as file:
            file.write(new_content)
        print(f"Patched JSON parsing in {f}")
