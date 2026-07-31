import sys
import os
from dotenv import load_dotenv
import requests

env_path = os.path.join(os.path.dirname(__file__), "../backend/.env")
load_dotenv(dotenv_path=env_path)

print("--- Testing Providers ---", flush=True)

# 1. NVIDIA
nvidia_key = os.getenv("NVIDIA_API_KEY")
if nvidia_key:
    headers = {"Authorization": f"Bearer {nvidia_key}"}
    try:
        r = requests.get("https://integrate.api.nvidia.com/v1/models", headers=headers, timeout=5)
        print(f"NVIDIA: {r.status_code}")
    except Exception as e:
        print(f"NVIDIA Exception: {e}")
else:
    print("NVIDIA: NO KEY")

# 2. Azure
azure_end = os.getenv("AZURE_OPENAI_ENDPOINT")
azure_key = os.getenv("AZURE_OPENAI_KEY")
if azure_end and azure_key:
    headers = {"api-key": azure_key}
    try:
        url = f"{azure_end.rstrip('/')}/openai/deployments?api-version=2024-02-15-preview"
        r = requests.get(url, headers=headers, timeout=5)
        print(f"Azure: {r.status_code}")
    except Exception as e:
        print(f"Azure Exception: {e}")
else:
    print("Azure: NO KEY OR ENDPOINT")

# 3. Groq
groq_key = os.getenv("GROQ_API_KEY")
if groq_key:
    headers = {"Authorization": f"Bearer {groq_key}"}
    try:
        r = requests.get("https://api.groq.com/openai/v1/models", headers=headers, timeout=5)
        print(f"Groq: {r.status_code}")
    except Exception as e:
        print(f"Groq Exception: {e}")
else:
    print("Groq: NO KEY")

# 4. ADO
ado_org = os.getenv("ADO_ORGANIZATION") or os.getenv("ADO_ORG_URL")
ado_pat = os.getenv("ADO_PAT")
if ado_org and ado_pat:
    if not ado_org.startswith("http"): ado_org = f"https://{ado_org}"
    import base64
    auth = base64.b64encode(f":{ado_pat}".encode()).decode()
    headers = {"Authorization": f"Basic {auth}"}
    try:
        r = requests.get(f"{ado_org.rstrip('/')}/_apis/projects?api-version=7.1", headers=headers, timeout=10)
        print(f"ADO: {r.status_code}")
    except Exception as e:
        print(f"ADO Exception: {e}")
else:
    print("ADO: NO ORG OR PAT")

print("--- Done ---", flush=True)
