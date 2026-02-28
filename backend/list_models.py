import asyncio
from openai import AsyncOpenAI

FEATHERLESS_API_KEY = "rc_02a00b6e2146dbe53cfd19360dc8fd52a7a445baf629875ab8d00ec3b92f052b"
FEATHERLESS_BASE_URL = "https://api.featherless.ai/v1"

client = AsyncOpenAI(
    api_key=FEATHERLESS_API_KEY,
    base_url=FEATHERLESS_BASE_URL
)

async def check_models():
    models = await client.models.list()
    valid_models = []
    
    # Try to find a llama 3 or deepseek or mistral
    for model in models.data:
        m_id = model.id.lower()
        if "llama-3" in m_id or "deepseek" in m_id or "mistral" in m_id or "glm" in m_id or "qwen" in m_id:
            valid_models.append(model.id)
            
    print("Available matching models:")
    for v in valid_models[:20]: # Print top 20 matches
        print(v)

asyncio.run(check_models())
