from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol


class ChatLLM(Protocol):
    def generate(self, *, system: str, user: str) -> str: ...


@dataclass(slots=True)
class MockLLM:
    response: str = "mock persona response"
    calls: list[dict[str, str]] = field(default_factory=list)

    def generate(self, *, system: str, user: str) -> str:
        self.calls.append({"system": system, "user": user})
        return self.response
