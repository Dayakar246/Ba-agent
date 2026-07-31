import sys
import os
import asyncio
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), "../.env")
load_dotenv(dotenv_path=env_path)

sys.path.append(os.path.join(os.path.dirname(__file__), "../backend"))

from services.llm_service import LLMService
from services.ado_service import AzureDevOpsService

async def run_tests():
    print("--- 1. Testing LLM Providers ---")
    llm = LLMService()
    
    # Test Azure
    print("Testing Azure OpenAI...")
    try:
        if llm.azure_client:
            res = await llm.call("Say the word 'Hello'", provider="azure")
            print(f"Azure Response: {res[:20]}...")
        else:
            print("Azure Client NOT configured.")
    except Exception as e:
        print(f"Azure Error: {e}")

    # Test NVIDIA
    print("Testing NVIDIA Foundry...")
    try:
        res = await llm.call("Say the word 'Hello'", provider="nvidia")
        print(f"NVIDIA Response: {res[:20]}...")
    except Exception as e:
        print(f"NVIDIA Error: {e}")
        
    # Test Groq
    print("Testing Groq...")
    try:
        if llm.groq_clients:
            res = await llm.call("Say the word 'Hello'", provider="groq")
            print(f"Groq Response: {res[:20]}...")
        else:
            print("Groq Client NOT configured.")
    except Exception as e:
        print(f"Groq Error: {e}")

    print("\n--- 2. Testing Azure DevOps Connectivity ---")
    ado = AzureDevOpsService()
    print(f"ADO URL: {ado.org_url}")
    print(f"ADO Project: {ado.project}")
    try:
        # Get Iterations to verify PAT auth
        iterations = await ado.get_iterations()
        if iterations and "count" in iterations:
            print(f"ADO Connectivity SUCCESS: Found {iterations['count']} iterations.")
        else:
            print(f"ADO Iteration response: {iterations}")
    except Exception as e:
        print(f"ADO Error: {e}")

if __name__ == "__main__":
    asyncio.run(run_tests())
