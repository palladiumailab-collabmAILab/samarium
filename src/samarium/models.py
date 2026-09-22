from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True, slots=True)
class Post:
    id: str
    created_at: datetime
    text: str
    conversation_id: str | None = None
    in_reply_to_status_id: str | None = None
    in_reply_to_user_id: str | None = None
    is_reply: bool = False
    urls: tuple[str, ...] = ()
    hashtags: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["created_at"] = self.created_at.isoformat()
        data["urls"] = list(self.urls)
        data["hashtags"] = list(self.hashtags)
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Post":
        return cls(
            id=str(data["id"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            text=str(data["text"]),
            conversation_id=_none_or_str(data.get("conversation_id")),
            in_reply_to_status_id=_none_or_str(data.get("in_reply_to_status_id")),
            in_reply_to_user_id=_none_or_str(data.get("in_reply_to_user_id")),
            is_reply=bool(data.get("is_reply", False)),
            urls=tuple(str(x) for x in data.get("urls", ())),
            hashtags=tuple(str(x) for x in data.get("hashtags", ())),
        )


def _none_or_str(value: Any) -> str | None:
    return None if value is None else str(value)


@dataclass(frozen=True, slots=True)
class PersonaProfile:
    post_count: int
    reply_ratio: float
    avg_chars: float
    median_chars: float
    newline_ratio: float
    question_ratio: float
    exclamation_ratio: float
    top_ngrams: tuple[str, ...]
    top_hashtags: tuple[str, ...]

    def to_prompt(self) -> str:
        ngrams = ", ".join(self.top_ngrams) or "(none)"
        hashtags = ", ".join(f"#{x}" for x in self.top_hashtags) or "(none)"
        return "\n".join(
            [
                f"post_count={self.post_count}",
                f"reply_ratio={self.reply_ratio:.3f}",
                f"avg_chars={self.avg_chars:.1f}",
                f"median_chars={self.median_chars:.1f}",
                f"newline_ratio={self.newline_ratio:.3f}",
                f"question_ratio={self.question_ratio:.3f}",
                f"exclamation_ratio={self.exclamation_ratio:.3f}",
                f"frequent_char_ngrams={ngrams}",
                f"top_hashtags={hashtags}",
            ]
        )
