"""LLM service for generating responses.

Supports:
- Ollama (local)
- OpenAI-compatible APIs (remote)
"""

import os
from typing import AsyncIterator, Optional

import httpx
from pydantic import BaseModel


class LLMConfig(BaseModel):
    """LLM provider configuration."""

    provider: str  # "ollama" or "openai"
    base_url: str
    model: str
    api_key: Optional[str] = None
    timeout: int = 60


class LLMService:
    """Service for LLM inference.

    Wraps HTTP calls to LLM providers (Ollama, OpenAI-compatible APIs).
    Supports both sync and streaming generation.
    """

    def __init__(self, config: LLMConfig):
        """Initialize LLM service.

        Args:
            config: Provider configuration (base_url, model, api_key)
        """
        self.config = config
        self.client = httpx.AsyncClient(timeout=config.timeout)

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> str:
        """Generate a single response (non-streaming).

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Max tokens to generate

        Returns:
            Generated text response

        Raises:
            httpx.HTTPStatusError: If API returns error status
            httpx.TimeoutException: If request times out
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        if self.config.provider == "ollama":
            url = f"{self.config.base_url}/api/chat"
            payload = {
                "model": self.config.model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens,
                },
            }
        else:  # OpenAI-compatible
            url = f"{self.config.base_url}/chat/completions"
            payload = {
                "model": self.config.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": False,
            }

        headers = {}
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"

        response = await self.client.post(url, json=payload, headers=headers)
        response.raise_for_status()

        data = response.json()

        if self.config.provider == "ollama":
            return data["message"]["content"]
        else:  # OpenAI-compatible
            return data["choices"][0]["message"]["content"]

    async def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> AsyncIterator[str]:
        """Generate response with streaming (yields tokens incrementally).

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Max tokens to generate

        Yields:
            Token strings as they are generated

        Raises:
            httpx.HTTPStatusError: If API returns error status
            httpx.TimeoutException: If request times out
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        if self.config.provider == "ollama":
            url = f"{self.config.base_url}/api/chat"
            payload = {
                "model": self.config.model,
                "messages": messages,
                "stream": True,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens,
                },
            }
        else:  # OpenAI-compatible
            url = f"{self.config.base_url}/chat/completions"
            payload = {
                "model": self.config.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": True,
            }

        headers = {}
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"

        async with self.client.stream("POST", url, json=payload, headers=headers) as response:
            response.raise_for_status()

            async for line in response.aiter_lines():
                if not line.strip():
                    continue

                # Remove "data: " prefix if present (OpenAI format)
                if line.startswith("data: "):
                    line = line[6:]

                # OpenAI sends [DONE] as final message
                if line == "[DONE]":
                    break

                try:
                    import json

                    data = json.loads(line)

                    if self.config.provider == "ollama":
                        if "message" in data and "content" in data["message"]:
                            yield data["message"]["content"]
                        if data.get("done", False):
                            break
                    else:  # OpenAI-compatible
                        if "choices" in data and len(data["choices"]) > 0:
                            delta = data["choices"][0].get("delta", {})
                            if "content" in delta:
                                yield delta["content"]
                except json.JSONDecodeError:
                    # Skip malformed lines
                    continue

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


def get_llm_service() -> LLMService:
    """Factory function to create LLM service from environment variables.

    Environment variables:
        LLM_PROVIDER: "ollama" or "openai"
        LLM_BASE_URL: Base URL for API
        LLM_MODEL: Model name
        LLM_API_KEY: API key (optional, for OpenAI-compatible)

    Returns:
        Configured LLMService instance

    Raises:
        ValueError: If required env vars are missing
    """
    provider = os.getenv("LLM_PROVIDER", "ollama")
    base_url = os.getenv("LLM_BASE_URL")
    model = os.getenv("LLM_MODEL")
    api_key = os.getenv("LLM_API_KEY")

    if not base_url:
        raise ValueError("LLM_BASE_URL environment variable is required")
    if not model:
        raise ValueError("LLM_MODEL environment variable is required")

    config = LLMConfig(
        provider=provider,
        base_url=base_url,
        model=model,
        api_key=api_key,
    )

    return LLMService(config)
