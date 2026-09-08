import asyncio
import os

from openai import AsyncOpenAI


async def main():
    client = AsyncOpenAI(
        base_url="https://devops-maf4.services.ai.azure.com/openai/v1",
        api_key=os.environ["AZURE_OPENAI_API_KEY"],
    )
    try:
        response = await client.chat.completions.create(
            model="Llama-3.3-70B-Instruct",
            messages=[{"role": "user", "content": "Test"}],
            max_tokens=10,
        )
        print("Success:", response.choices[0].message.content)
    except Exception as e:
        print("Error:", e)


asyncio.run(main())import asyncio
import os
from openai import AsyncOpenAI
import httpx

async def main():
    client = AsyncOpenAI(
        base_url="https://devops-maf4.services.ai.azure.com/openai/v1",
        api_key=os.environ["AZURE_OPENAI_API_KEY"]
    )
    try:
        response = await client.chat.completions.create(
            model="Llama-3.3-70B-Instruct",
            messages=[{"role": "user", "content": "Test"}],
            max_tokens=10
        )
        print("Success:", response.choices[0].message.content)
    except Exception as e:
        print("Error:", e)

asyncio.run(main())
