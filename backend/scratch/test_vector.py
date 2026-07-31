import asyncio
import os
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), "../.env")
load_dotenv(dotenv_path=env_path)

from agents.knowledge_agent import KnowledgeAgent

async def test():
    ka = KnowledgeAgent()
    res = await ka.retrieve_relevant_context("What are the rules for modifying a BOP policy midterm?", lob="General")
    print("\n--- RESULT ---")
    print(res)

asyncio.run(test())
