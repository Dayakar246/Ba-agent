import os
import base64
import httpx
from dotenv import load_dotenv

load_dotenv('backend/.env')

url = os.getenv("ADO_ORG_URL", "").rstrip("/")
proj = os.getenv("ADO_PROJECT", "")
pat = os.getenv("ADO_PAT", "")

auth = base64.b64encode(f":{pat}".encode()).decode()

query = {"query": f"SELECT [System.Id] FROM workitems WHERE [System.TeamProject] = '{proj}'"}

res = httpx.post(
    f"{url}/{proj}/_apis/wit/wiql?api-version=7.1",
    headers={'Authorization': f'Basic {auth}', 'Content-Type': 'application/json'},
    json=query
)

print('STATUS:', res.status_code)
print('TEXT:', res.text[:200])
