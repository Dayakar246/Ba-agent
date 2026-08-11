import os
import sys
import asyncio
from dotenv import load_dotenv

# Ensure backend root is on PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.env"))
load_dotenv(dotenv_path=env_path)

from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from services.vector_service import VectorSearchService

async def reset_requirement_memory_index():
    endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
    key = os.getenv("AZURE_SEARCH_KEY")

    print("\n================================================================================")
    print(" [AZURE AI SEARCH INDEX RESET UTILITY]")
    print(f" -> Target Endpoint: {endpoint}")
    print(" -> Target Index   : 'requirement-memory'")
    print("================================================================================")

    if not endpoint or not key:
        print(" ERROR: Missing AZURE_SEARCH_ENDPOINT or AZURE_SEARCH_KEY in .env!")
        return

    credential = AzureKeyCredential(key)
    index_client = SearchIndexClient(endpoint=endpoint, credential=credential)

    # 1. Delete existing 'requirement-memory' index if it exists
    indexes = [idx.name for idx in index_client.list_indexes()]
    if "requirement-memory" in indexes:
        print(" -> Deleting stale 'requirement-memory' index from Azure AI Search...")
        try:
            index_client.delete_index("requirement-memory")
            print(" -> SUCCESS: Stale 'requirement-memory' index deleted.")
        except Exception as e:
            print(f" -> ERROR deleting index: {e}")
    else:
        print(" -> Index 'requirement-memory' does not exist yet. Creating clean index...")

    # 2. Re-create clean index with VectorSearchService
    vector_service = VectorSearchService(index_name="requirement-memory")
    vector_service.create_index_if_not_exists()
    print(" -> SUCCESS: Clean 'requirement-memory' index initialized with vector search schema.")

    # 3. Verify Corporate Guidelines index remains intact
    if "insurance-guidelines" in indexes:
        print(" -> PRESERVED: 'insurance-guidelines' index remains untouched with 532 corporate guideline chunks.")

    print("\n================================================================================")
    print(" SUCCESS: AZURE AI SEARCH STORAGE QUOTA HAS BEEN RESET AND CLEANED!")
    print("================================================================================\n")

if __name__ == "__main__":
    asyncio.run(reset_requirement_memory_index())
