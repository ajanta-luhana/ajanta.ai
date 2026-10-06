import json
from collections.abc import AsyncIterator

import httpx

from app.core.config import get_settings


async def stream_completion(system: str, user: str) -> AsyncIterator[str]:
    s = get_settings()
    payload = {"model": s.openai_model, "stream": True, "temperature": 0.2,
               "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}
    headers = {"Authorization": f"Bearer {s.openai_api_key}"}
    async with httpx.AsyncClient(timeout=60) as client:
        async with client.stream("POST", f"{s.openai_base_url}/chat/completions", json=payload, headers=headers) as r:
            r.raise_for_status()
            async for line in r.aiter_lines():
                if not line.startswith("data: ") or line.endswith("[DONE]"):
                    continue
                delta = json.loads(line[6:])["choices"][0]["delta"].get("content")
                if delta:
                    yield delta


def llm_available() -> bool:
    return bool(get_settings().openai_api_key)
