"""Parse an official X archive without executing its JavaScript wrapper."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Iterable, Mapping

from .models import CanonicalPost, parse_x_datetime

_JS_ASSIGNMENT = re.compile(r"^\s*window\.YTD\.[\w.]+\s*=\s*", re.DOTALL)
_URL_ONLY = re.compile(r"^(?:https?://\S+\s*)+$", re.IGNORECASE)
_AUTOMATED = re.compile(
    r"(?:posted\s+automatically|自動投稿|botによる投稿|#nowplaying\s+https?://)",
    re.IGNORECASE,
)


def load_x_archive(path: str | Path) -> list[CanonicalPost]:
    """Load, normalize, filter, and chronologically sort an X tweets.js file."""
    raw = Path(path).read_text(encoding="utf-8-sig")
    payload = _JS_ASSIGNMENT.sub("", raw, count=1).strip()
    if payload.endswith(";"):
        payload = payload[:-1]
    parsed = json.loads(payload)
    if not isinstance(parsed, list):
        raise ValueError("X archive payload must be a JSON array")
    return normalize_posts(parsed)


def write_canonical_jsonl(posts: Iterable[CanonicalPost], path: str | Path) -> None:
    """Write canonical posts as UTF-8 JSON Lines for local downstream use."""
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8", newline="\n") as stream:
        for post in posts:
            stream.write(json.dumps(post.to_dict(), ensure_ascii=False, sort_keys=True))
            stream.write("\n")


def normalize_posts(records: Iterable[Mapping[str, Any]]) -> list[CanonicalPost]:
    posts: list[CanonicalPost] = []
    seen_ids: set[str] = set()
    seen_text: set[str] = set()

    for record in records:
        tweet = record.get("tweet", record)
        if not isinstance(tweet, Mapping):
            continue
        post = _canonicalize(tweet)
        if post is None:
            continue
        normalized_text = " ".join(post.text.casefold().split())
        if post.id in seen_ids or normalized_text in seen_text:
            continue
        seen_ids.add(post.id)
        seen_text.add(normalized_text)
        posts.append(post)

    return sorted(posts, key=lambda post: (post.created_at, post.id))


def _canonicalize(tweet: Mapping[str, Any]) -> CanonicalPost | None:
    text = str(tweet.get("full_text") or tweet.get("text") or "").strip()
    if not text or text.startswith("RT @") or _URL_ONLY.fullmatch(text) or _AUTOMATED.search(text):
        return None

    post_id = str(tweet.get("id_str") or tweet.get("id") or "").strip()
    created_at = str(tweet.get("created_at") or "").strip()
    if not post_id or not created_at:
        return None

    entities = tweet.get("entities") if isinstance(tweet.get("entities"), Mapping) else {}
    urls = tuple(
        str(item.get("expanded_url") or item.get("url"))
        for item in entities.get("urls", [])
        if isinstance(item, Mapping) and (item.get("expanded_url") or item.get("url"))
    )
    hashtags = tuple(
        str(item.get("text"))
        for item in entities.get("hashtags", [])
        if isinstance(item, Mapping) and item.get("text")
    )
    reply_status = _optional_string(tweet.get("in_reply_to_status_id_str") or tweet.get("in_reply_to_status_id"))
    reply_user = _optional_string(tweet.get("in_reply_to_user_id_str") or tweet.get("in_reply_to_user_id"))

    return CanonicalPost(
        id=post_id,
        created_at=parse_x_datetime(created_at),
        text=text,
        conversation_id=_optional_string(tweet.get("conversation_id_str") or tweet.get("conversation_id")),
        in_reply_to_status_id=reply_status,
        in_reply_to_user_id=reply_user,
        is_reply=reply_status is not None or reply_user is not None,
        urls=urls,
        hashtags=hashtags,
    )


def _optional_string(value: object) -> str | None:
    if value is None or value == "":
        return None
    return str(value)
