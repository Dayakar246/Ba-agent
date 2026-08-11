import os
import sys
import asyncio
import hashlib
from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.env"))
load_dotenv(dotenv_path=env_path)

from agents.knowledge_agent import KnowledgeAgent
from services.vector_service import VectorSearchService

async def test_upsert_replacement():
    ka = KnowledgeAgent()
    vs = VectorSearchService()

    print("\n================================================================================")
    print(" [TEST: KNOWLEDGE AGENT AZURE SEARCH REPLACEMENT / UPSERT VERIFICATION]")
    print("================================================================================")

    # Simulated BRD PDF Content & SHA-256 hash
    sample_pdf_bytes = b"Commercial Property Risk Assessment Test BRD Content v1.0"
    file_hash = hashlib.sha256(sample_pdf_bytes).hexdigest()
    deterministic_proj_id = f"doc_{file_hash[:16]}"
    
    print(f" -> Simulated File SHA-256 : {file_hash}")
    print(f" -> Azure Search Project Key: {deterministic_proj_id}")

    sample_extraction_v1 = {
        "functional_requirements": [
            {
                "id": "FR-001",
                "description": "Version 1: System shall capture commercial property square footage.",
                "priority": "High"
            }
        ]
    }

    sample_extraction_v2 = {
        "functional_requirements": [
            {
                "id": "FR-001",
                "description": "Version 2 (REPLACED): System shall capture commercial property square footage and building age.",
                "priority": "High"
            }
        ]
    }

    # 1. FIRST UPLOAD INGESTION
    print("\n--- STEP 1: Executing Ingestion #1 (First Upload of BRD) ---")
    doc_id_1 = "doc_upload_session_1"
    await ka.ingest_project_requirements(doc_id=doc_id_1, extraction=sample_extraction_v1, lob="Commercial Property", project_id=deterministic_proj_id)

    # Verify document in Azure AI Search after Ingestion #1
    primary_key = f"{deterministic_proj_id}_FR-001"
    try:
        doc_v1 = vs.search_client.get_document(key=primary_key)
        print(f" -> Azure Search Document fetched for Key '{primary_key}':")
        print(f"   * Key: {doc_v1.get('id')} | Content: \"{doc_v1.get('content')}\"")
    except Exception as e:
        print(f" ERROR fetching document after Upload #1: {e}")

    # 2. SECOND UPLOAD INGESTION (RE-UPLOAD OF SAME BRD)
    print("\n--- STEP 2: Executing Ingestion #2 (Re-upload of same BRD with updated pipeline code) ---")
    doc_id_2 = "doc_upload_session_2" # Different session doc_id, but same file_hash
    await ka.ingest_project_requirements(doc_id=doc_id_2, extraction=sample_extraction_v2, lob="Commercial Property", project_id=deterministic_proj_id)

    # Verify document in Azure AI Search after Ingestion #2
    try:
        doc_v2 = vs.search_client.get_document(key=primary_key)
        print(f" -> Azure Search Document fetched for Key '{primary_key}' after Upload #2:")
        print(f"   * Key: {doc_v2.get('id')} | Content: \"{doc_v2.get('content')}\"")
        
        # Check total documents in requirement-memory index
        total_count = vs.search_client.search(search_text="*", include_total_count=True).get_count()
        print(f" -> Total Requirement Documents in 'requirement-memory' Index: {total_count}")

        print("\n--- STEP 3: Verification Analysis ---")
        if "Version 2 (REPLACED)" in doc_v2.get("content", ""):
            print(" SUCCESS: Requirement FR-001 was REPLACED in-place in Azure AI Search!")
            print(f"          Primary Key '{primary_key}' updated seamlessly. Storage quota remains clean.")
        else:
            print(" FAILED: Replacement content not found.")
    except Exception as e:
        print(f" ERROR fetching document after Upload #2: {e}")

    print("\n================================================================================")
    print(" [TEST COMPLETE - NO CODE WAS CHANGED]")
    print("================================================================================\n")

if __name__ == "__main__":
    asyncio.run(test_upsert_replacement())
