import asyncio
import os
from dotenv import load_dotenv

# Load env
env_path = os.path.join(os.path.dirname(__file__), "../.env")
load_dotenv(dotenv_path=env_path)

from services.vector_service import VectorSearchService

async def run_test():
    vs = VectorSearchService()
    # Create a dummy 1536-dim vector
    dummy_vector = [0.1] * 1536
    
    print("Testing search_memory...")
    try:
        res1 = await vs.search_memory(dummy_vector, top=1)
        print("search_memory success:", res1)
    except Exception as e:
        print("search_memory ERROR:", e)

    print("\nTesting search_guidelines...")
    try:
        res2 = await vs.search_guidelines(dummy_vector, lob="General", top=1)
        print("search_guidelines success:", res2)
    except Exception as e:
        print("search_guidelines ERROR:", e)

if __name__ == "__main__":
    asyncio.run(run_test())
