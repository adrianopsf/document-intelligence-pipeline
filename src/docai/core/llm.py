"""OpenAI-compatible LLM client abstraction.

Works with any OpenAI-compatible API: OpenAI, Ollama, vLLM, LiteLLM, etc.
"""

from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from docai.config import settings
from docai.core.logging import get_logger

logger = get_logger(__name__)

_client: AsyncOpenAI | None = None


def get_llm_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI(
            api_key=settings.llm_api_key,
            base_url=settings.llm_base_url,
        )
    return _client


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def llm_completion(
    prompt: str,
    system_prompt: str = "You are a document analysis assistant.",
    temperature: float = 0.1,
    max_tokens: int = 2000,
) -> str:
    client = get_llm_client()
    response = await client.chat.completions.create(
        model=settings.llm_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    content = response.choices[0].message.content
    if content is None:
        return ""
    return content.strip()


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def llm_json_completion(
    prompt: str,
    system_prompt: str = "You are a document analysis assistant. Always respond with valid JSON.",
    temperature: float = 0.0,
    max_tokens: int = 2000,
) -> str:
    client = get_llm_client()
    response = await client.chat.completions.create(
        model=settings.llm_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
        response_format={"type": "json_object"},
    )
    content = response.choices[0].message.content
    if content is None:
        return "{}"
    return content.strip()
