import asyncio
from app.config import settings
from app.providers.llm_provider import get_llm_provider

async def test():
    print("Testing get_llm_provider with Gemini...")
    provider = get_llm_provider(settings)
    print("Provider:", type(provider).__name__)
    
    text = await provider.generate("Give me 3 keywords for AI crop diagnosis")
    print("Generated text:\n", text.strip())
    
    data = await provider.generate_json("Return a JSON with key 'status'='active' and list 'items'=['a','b']")
    print("Generated JSON:\n", data)

if __name__ == "__main__":
    asyncio.run(test())
