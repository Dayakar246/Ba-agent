import asyncio
from openai import AsyncAzureOpenAI

async def main():
    client = AsyncAzureOpenAI(
        azure_endpoint="https://azureopenai-backofficeapiservice.openai.azure.com/",
        api_key="69156c1821c84e42993f9d6df78c452e",
        api_version="2025-01-01-preview"
    )
    try:
        response = await client.chat.completions.create(
            model="chatbotdemo",
            messages=[{"role": "user", "content": "Test"}],
            max_tokens=10
        )
        print("Success:", response.choices[0].message.content)
    except Exception as e:
        print("Error:", e)

asyncio.run(main())
