import os
import sys
import asyncio
from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.env"))
load_dotenv(dotenv_path=env_path)

from agents.knowledge_agent import KnowledgeAgent
from services.vector_service import VectorSearchService

async def trace_memory_flow():
    ka = KnowledgeAgent()
    vs = VectorSearchService()

    print("\n================================================================================")
    print("🔍 [END-TO-END RAG TRACE: REQUIREMENT-MEMORY INDEX]")
    print("================================================================================")

    # 1. Step 1: Ingest sample requirement into memory
    sample_extraction = {
        "functional_requirements": [
            {
                "id": "FR-014",
                "description": "The system shall capture automatic sprinkler percentage coverage (0-100%) for commercial properties.",
                "priority": "High"
            }
        ]
    }
    
    print("\n--- STEP 1: Ingesting Sample Requirement into 'requirement-memory' ---")
    doc_id = "test_project_commercial"
    await ka.ingest_project_requirements(doc_id=doc_id, extraction=sample_extraction, lob="Commercial Property", project_id="proj_comm_001")

    # 2. Step 2: Query for a similar requirement
    query_text = "Does the system collect automatic sprinkler coverage percentage for commercial buildings?"
    print(f"\n--- STEP 2: Executing Query to Azure AI Search ---")
    print(f" ► Raw Query Text: \"{query_text}\"")

    query_vector = await ka._get_embedding(query_text)
    print(f" ► Generated 1536-dim Embedding Vector (First 5 values: {query_vector[:5]}...)")

    # Direct search on requirement-memory to inspect scores
    results = vs.search_client.search(
        search_text=None,
        vector_queries=[{
            "kind": "vector",
            "vector": query_vector,
            "fields": "content_vector",
            "k": 3
        }],
        select=["content", "lob", "requirement_id", "doc_id"]
    )

    retrieved_items = [r for r in results]
    print(f"\n--- STEP 3: Retrieved Documents & Search Similarity Scores ---")
    print(f" ► Number of matching items retrieved: {len(retrieved_items)}")
    for idx, r in enumerate(retrieved_items, 1):
        score = r.get("@search.score", 0.0)
        req_id = r.get("requirement_id")
        doc = r.get("doc_id")
        lob = r.get("lob")
        content = r.get("content")
        print(f"\n [{idx}] Azure Primary Key `id` : {r.get('id')}")
        print(f"     Similarity Score (@search.score): {score:.4f} ({score * 100:.2f}% Match)")
        print(f"     Requirement ID                   : {req_id}")
        print(f"     Doc ID                           : {doc}")
        print(f"     Line of Business (LOB)           : {lob}")
        print(f"     Requirement Content              : \"{content}\"")

    # 3. Step 4: Show exact RAG context block passed to LLM prompt
    context_block = await ka.retrieve_relevant_context(query_text, lob="Commercial Property", n_results=3)

    print(f"\n--- STEP 4: Exact Context Block & LLM Prompt Integration ---")
    print(" ► Format injected into LLM Prompt (e.g. inside FunctionalSpecAgent / GapAnalysis):")
    print("--------------------------------------------------------------------------------")
    print(context_block)
    print("--------------------------------------------------------------------------------")

    print("\n================================================================================")
    print("✅ [TRACE COMPLETE]")
    print("================================================================================\n")

if __name__ == "__main__":
    asyncio.run(trace_memory_flow())
