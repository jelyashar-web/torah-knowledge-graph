"""
Multi-provider LLM client for Torah Knowledge Graph AI Discovery.

Supports:
  - Ollama (local)
  - Anthropic Claude (Claude 4 Sonnet/Opus)
  - OpenRouter (proxy for multiple models including Kimi)
  - OpenAI (fallback)

Usage:
    from app.ai_client import LLMClient
    client = LLMClient(provider="claude")
    response = await client.complete("Find relationships between Moses and Aaron in Exodus")
"""

import json
from typing import Any

import httpx
import structlog

from app.config import settings

logger = structlog.get_logger()


class LLMClient:
    """Unified LLM client with multi-provider support."""

    def __init__(self, provider: str | None = None):
        self.provider = (provider or settings.ai_provider or "ollama").lower()
        self._http = httpx.AsyncClient(timeout=120.0)

    async def complete(
        self,
        prompt: str,
        system: str | None = None,
        temperature: float = 0.2,
        max_tokens: int = 4000,
        json_mode: bool = False,
    ) -> dict[str, Any]:
        """Send a completion request to the configured provider."""
        if self.provider == "claude":
            return await self._claude_complete(prompt, system, temperature, max_tokens)
        elif self.provider == "openrouter":
            return await self._openrouter_complete(prompt, system, temperature, max_tokens, json_mode)
        elif self.provider == "openai":
            return await self._openai_complete(prompt, system, temperature, max_tokens, json_mode)
        else:
            return await self._ollama_complete(prompt, system, temperature, max_tokens, json_mode)

    async def _claude_complete(
        self, prompt: str, system: str | None, temperature: float, max_tokens: int
    ) -> dict[str, Any]:
        """Call Anthropic Claude API."""
        headers = {
            "x-api-key": settings.anthropic_api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        payload = {
            "model": settings.claude_model or "claude-sonnet-4-6-20251001",
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system:
            payload["system"] = system

        response = await self._http.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=payload,
        )
        response.raise_for_status()
        data = response.json()

        return {
            "text": data["content"][0]["text"],
            "model": data["model"],
            "usage": data.get("usage", {}),
            "provider": "claude",
        }

    async def _openrouter_complete(
        self, prompt: str, system: str | None, temperature: float, max_tokens: int, json_mode: bool
    ) -> dict[str, Any]:
        """Call OpenRouter API (supports Kimi, Claude, GPT, etc.)."""
        headers = {
            "Authorization": f"Bearer {settings.openrouter_api_key}",
            "Content-Type": "application/json",
        }
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": settings.openrouter_model or "anthropic/claude-sonnet-4-6",
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        response = await self._http.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
        )
        response.raise_for_status()
        data = response.json()

        return {
            "text": data["choices"][0]["message"]["content"],
            "model": data["model"],
            "usage": data.get("usage", {}),
            "provider": "openrouter",
        }

    async def _openai_complete(
        self, prompt: str, system: str | None, temperature: float, max_tokens: int, json_mode: bool
    ) -> dict[str, Any]:
        """Call OpenAI API."""
        headers = {
            "Authorization": f"Bearer {settings.openai_api_key}",
            "Content-Type": "application/json",
        }
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": settings.openai_model or "gpt-4o",
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        response = await self._http.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload,
        )
        response.raise_for_status()
        data = response.json()

        return {
            "text": data["choices"][0]["message"]["content"],
            "model": data["model"],
            "usage": data.get("usage", {}),
            "provider": "openai",
        }

    async def _ollama_complete(
        self, prompt: str, system: str | None, temperature: float, max_tokens: int, json_mode: bool
    ) -> dict[str, Any]:
        """Call local Ollama API."""
        payload = {
            "model": settings.ollama_model or "llama3.2",
            "prompt": prompt,
            "system": system or "",
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }

        response = await self._http.post(
            f"{settings.ollama_base_url or 'http://localhost:11434'}/api/generate",
            json=payload,
        )
        response.raise_for_status()
        data = response.json()

        return {
            "text": data["response"],
            "model": data["model"],
            "usage": {"prompt_tokens": data.get("prompt_eval_count", 0), "completion_tokens": data.get("eval_count", 0)},
            "provider": "ollama",
        }

    async def discover_relationships(
        self,
        source_text: str,
        source_ref: str,
        existing_entities: list[dict] | None = None,
    ) -> dict[str, Any]:
        """Use LLM to discover relationships in a Torah text segment."""
        system = """You are a Torah scholar AI. Extract structured relationships from Jewish texts.
Return ONLY valid JSON. Do not include markdown formatting or commentary outside the JSON."""

        entity_context = ""
        if existing_entities:
            entity_context = "\nKnown entities in this text:\n" + json.dumps(existing_entities, ensure_ascii=False, indent=2)

        prompt = f"""Analyze this Torah text and extract all meaningful relationships.

Text ({source_ref}):
{source_text[:2000]}
{entity_context}

Extract:
1. Entities (people, places, concepts, mitzvot)
2. Relationships between them with evidence quotes
3. Cross-references to other texts if mentioned

Return JSON with this structure:
{{
  "entities": [
    {{"name": "...", "nameHe": "...", "type": "Person|Place|Concept|Mitzvah|Event", "role": "..."}}
  ],
  "relationships": [
    {{
      "source": "...",
      "target": "...",
      "type": "MENTIONS|CITES|COMMENTARY_ON|TEACHES|OCCURRED_AT|PARTICIPATED_IN",
      "confidence": 0.0-1.0,
      "explanation": "...",
      "evidence": "..."
    }}
  ],
  "cross_references": [
    {{"ref": "Genesis 1:1", "context": "..."}}
  ]
}}"""

        result = await self.complete(prompt, system=system, json_mode=True)
        try:
            parsed = json.loads(result["text"])
            return {
                "discovery": parsed,
                "metadata": {
                    "provider": result["provider"],
                    "model": result["model"],
                    "source_ref": source_ref,
                    "usage": result.get("usage", {}),
                },
            }
        except json.JSONDecodeError:
            return {
                "discovery": {"error": "Failed to parse LLM response", "raw": result["text"][:500]},
                "metadata": {"provider": result["provider"], "model": result["model"]},
            }
