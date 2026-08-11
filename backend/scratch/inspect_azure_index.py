import os
import sys
import asyncio
from dotenv import load_dotenv

# Ensure backend root is on PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.env"))
load_dotenv(dotenv_path=env_path)

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient

async def inspect_azure_search():
    endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
    key = os.getenv("AZURE_SEARCH_KEY")

    print("\n================================================================================")
    print(" [AZURE AI SEARCH READ-ONLY INSPECTION]")
    print(f" -> Search Endpoint: {endpoint}")
    print("================================================================================")

    if not endpoint or not key:
        print(" ERROR: Missing AZURE_SEARCH_ENDPOINT or AZURE_SEARCH_KEY in .env!")
        return

    credential = AzureKeyCredential(key)
    index_client = SearchIndexClient(endpoint=endpoint, credential=credential)

    # 1. List All Active Indexes
    print("\n--- [1. Active Search Indexes Schema Inspection] ---")
    indexes = list(index_client.list_indexes())
    index_names = [idx.name for idx in indexes]
    print(f" -> Found {len(indexes)} active index(es) on Azure AI Search:")
    for idx_name in index_names:
        print(f"   * {idx_name}")

    # 2. Inspect 'requirement-memory' Index
    if "requirement-memory" in index_names:
        print("\n--- [2. 'requirement-memory' Index Document Breakdown] ---")
        client = SearchClient(endpoint=endpoint, index_name="requirement-memory", credential=credential)
        
        try:
            # Query all documents (wildcard search)
            results = client.search(
                search_text="*",
                select=["id", "doc_id", "requirement_id", "lob"],
                include_total_count=True
            )
            
            total_count = results.get_count()
            print(f" -> Total Requirement Documents in 'requirement-memory': {total_count}")

            doc_id_counts = {}
            lob_counts = {}
            sample_docs = []

            for i, item in enumerate(results):
                doc_id = item.get("doc_id", "UnknownDoc")
                lob = item.get("lob", "General")
                
                doc_id_counts[doc_id] = doc_id_counts.get(doc_id, 0) + 1
                lob_counts[lob] = lob_counts.get(lob, 0) + 1
                
                if i < 5:
                    sample_docs.append(item)

            print(f" -> Total Unique `doc_id` UUID Groups: {len(doc_id_counts)}")
            print("\n [Breakdown of Documents by doc_id / Upload Group]:")
            for d_id, cnt in sorted(doc_id_counts.items(), key=lambda x: x[1], reverse=True)[:15]:
                print(f"   - doc_id: {d_id}  -->  {cnt} requirements")
            
            if len(doc_id_counts) > 15:
                print(f"   ... and {len(doc_id_counts) - 15} more doc_id groups")

            print("\n [Breakdown of Documents by Line of Business (LOB)]:")
            for lob_name, cnt in lob_counts.items():
                print(f"   - LOB: {lob_name}  -->  {cnt} requirements")

            print("\n [Sample Document Primary Keys in Azure Search]:")
            for s in sample_docs:
                print(f"   - Azure Key `id`: {s.get('id')} | Req: {s.get('requirement_id')} | doc_id: {s.get('doc_id')}")

        except Exception as e:
            print(f" ERROR querying 'requirement-memory': {e}")
    else:
        print("\n [INFO] Index 'requirement-memory' does not exist yet on Azure Search.")

    # 3. Inspect 'insurance-guidelines' Index
    if "insurance-guidelines" in index_names:
        print("\n--- [3. 'insurance-guidelines' Index Inspection] ---")
        client = SearchClient(endpoint=endpoint, index_name="insurance-guidelines", credential=credential)
        try:
            results = client.search(
                search_text="*",
                select=["id", "doc_id", "lob", "category"],
                include_total_count=True
            )
            total_count = results.get_count()
            print(f" -> Total Corporate Guideline Documents in 'insurance-guidelines': {total_count}")
            
            g_doc_counts = {}
            for item in results:
                g_doc = item.get("doc_id", "Unknown")
                g_doc_counts[g_doc] = g_doc_counts.get(g_doc, 0) + 1
            
            print(" [Breakdown of Guidelines by Source File]:")
            for g_name, cnt in g_doc_counts.items():
                print(f"   - File: {g_name}  -->  {cnt} guideline chunks")
        except Exception as e:
            print(f" ERROR querying 'insurance-guidelines': {e}")
    else:
        print("\n [INFO] Index 'insurance-guidelines' does not exist yet on Azure Search.")

    print("\n================================================================================")
    print(" [INSPECTION COMPLETE - NO DATA WAS MODIFIED OR DELETED]")
    print("================================================================================\n")

if __name__ == "__main__":
    asyncio.run(inspect_azure_search())
