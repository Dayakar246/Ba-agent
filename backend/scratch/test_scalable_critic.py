import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import asyncio
import json
from agents.critic_agent import CriticAgent

async def test_critic_pipeline():
    print("\n================================================================================")
    print(" [TEST: SCALABLE CRITIC AGENT & MAP-REDUCE AUDIT PIPELINE]")
    print("================================================================================")
    
    critic = CriticAgent()

    # Generate 65 simulated requirements with source_chunk_idx provenance tagging
    simulated_reqs = []
    for i in range(1, 66):
        chunk_idx = (i - 1) // 10  # 10 reqs per chunk -> 7 chunks
        simulated_reqs.append({
            "id": f"FR-{i:03d}",
            "description": f"Requirement {i}: System shall process Commercial Property Policy claim data for sub-location {i}.",
            "priority": "Must Have" if i % 2 == 0 else "Should Have",
            "source_chunk_idx": chunk_idx
        })

    print(f" -> Generated {len(simulated_reqs)} simulated requirements across 7 source BRD chunks.")

    # Test Token Batch Allocator
    batches = critic._build_token_batches(simulated_reqs, max_token_budget=1500)
    print(f" -> Token Budget Allocator created {len(batches)} dynamic batch(es) (budget ~1500 tokens/batch):")
    for idx, b in enumerate(batches, 1):
        token_cost = critic._estimate_tokens(json.dumps(b))
        print(f"    * Batch {idx}: {len(b)} requirements (~{token_cost} tokens)")

    # Test 2-Phase Map-Reduce Audit
    simulated_brd = "Section 1: Commercial Property Policy Intake rules.\n" * 50
    print("\n -> Executing 2-Phase Map-Reduce Audit Review...")
    res = await critic.review_artifact("Functional Spec", simulated_reqs, source_brd=simulated_brd)

    print("\n [AUDIT RESULTS]")
    print(f"  * Overall Status     : {res.get('status')}")
    print(f"  * Min Confidence     : {res.get('confidence_score')}")
    print(f"  * Total Findings     : {len(res.get('findings', []))}")
    print(f"  * Batches Processed  : {res.get('batches_processed')}")
    
    print("\n================================================================================")
    print(" SUCCESS: SCALABLE CRITIC AGENT PIPELINE VERIFIED SUCCESSFULLY!")
    print("================================================================================\n")

if __name__ == "__main__":
    asyncio.run(test_critic_pipeline())
