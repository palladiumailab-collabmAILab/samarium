"""Stable data contracts shared by ingestion, retrieval, and providers."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping


@dataclass(frozen=True, slots=True)
class CanonicalPost:
    id: str
    created_at: datetime
    text: str
    conversation_id: str | None = None
    in_reply_to_status_id: str | None = None
    in_reply_to_user_id: str | None = None
    is_reply: bool = False
    urls: tuple[str, ...] = ()
    hashtags: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("post id must not be empty")
        if not self.text.strip():
            raise ValueError("post text must not be empty")
        if self.created_at.tzinfo is None:
            raise ValueError("created_at must be timezone-aware")

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "created_at": self.created_at.astimezone(timezone.utc).isoformat(),
            "text": self.text,
            "conversation_id": self.conversation_id,
            "in_reply_to_status_id": self.in_reply_to_status_id,
            "in_reply_to_user_id": self.in_reply_to_user_id,
            "is_reply": self.is_reply,
            "urls": list(self.urls),
            "hashtags": list(self.hashtags),
        }


@dataclass(frozen=True, slots=True)
class PersonaProfile:
    post_count: int
    average_length: float
    reply_ratio: float
    frequent_terms: tuple[tuple[str, int], ...]
    punctuation: Mapping[str, float]
    emoji: tuple[tuple[str, int], ...]
    first_person: tuple[tuple[str, int], ...]
    typical_phrases: tuple[tuple[str, int], ...]
    topics: tuple[tuple[str, int], ...]


@dataclass(frozen=True, slots=True)
class LLMRequest:
    system_prompt: str
    user_prompt: str
    metadata: Mapping[str, Any] = field(default_factory=dict)


def parse_x_datetime(value: str) -> datetime:
    """Parse both X export timestamps and ISO-8601 timestamps."""
    try:
        return datetime.strptime(value, "%a %b %d %H:%M:%S %z %Y")
    except ValueError:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            raise ValueError("created_at must include a timezone")
        return parsed
