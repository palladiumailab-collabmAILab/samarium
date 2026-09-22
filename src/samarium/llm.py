"""Provider boundary for generation, plus an offline deterministic mock."""

from __future__ import annotations

from typing import Protocol

from .models import LLMRequest


class LLMProvider(Protocol):
    def generate(self, request: LLMRequest) -> str: ...


class MockLLM:
    def generate(self, request: LLMRequest) -> str:
        example_count = len(request.metadata.get("example_ids", []))
        return f"[mock persona: {example_count} examples] {request.user_prompt}"
