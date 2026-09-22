from __future__ import annotations

import html
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Iterable

from .models import Post

_X_DATE = "%a %b %d %H:%M:%S %z %Y"
_URL_RE = re.compile(r"https?://\S+")


def load_x_archive(path: str | Path, *, skip_retweets: bool = True) -> list[Post]:
    """Load X archive tweets.js/JSON files into canonical posts.

    ``path`` can be a single file or an extracted archive directory. Real archive
    data should live outside Git or under ``data/private/``.
    """
    source = Path(path)
    files = _discover_files(source)
    posts: dict[str, Post] = {}
    for file in files:
        for post in _parse_archive_file(file, skip_retweets=skip_retweets):
            posts[post.id] = post
    return sorted(posts.values(), key=lambda p: (p.created_at, p.id))


def write_jsonl(posts: Iterable[Post], path: str | Path) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as fh:
        for post in posts:
            fh.write(json.dumps(post.to_dict(), ensure_ascii=False) + "\n")


def read_jsonl(path: str | Path) -> list[Post]:
    posts: list[Post] = []
    with Path(path).open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                posts.append(Post.from_dict(json.loads(line)))
    return posts


def _discover_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    if not path.exists():
        raise FileNotFoundError(path)
    candidates = [
        p
        for p in path.rglob("*")
        if p.is_file()
        and p.suffix.lower() in {".js", ".json"}
        and p.name.lower().startswith("tweets")
    ]
    if not candidates:
        raise FileNotFoundError(f"No tweet archive file found under {path}")
    return sorted(candidates)


def _parse_archive_file(path: Path, *, skip_retweets: bool) -> list[Post]:
    payload = _load_js_or_json(path)
    if isinstance(payload, dict):
        payload = payload.get("tweets", payload.get("data", []))
    if not isinstance(payload, list):
        raise ValueError(f"Unsupported archive structure: {path}")

    posts: list[Post] = []
    for item in payload:
        if not isinstance(item, dict):
            continue
        raw = item.get("tweet", item)
        if not isinstance(raw, dict):
            continue
        post = _canonicalize(raw)
        if skip_retweets and post.text.lstrip().startswith("RT @"):
            continue
        if _is_url_only(post.text):
            continue
        posts.append(post)
    return posts


def _load_js_or_json(path: Path):
    text = path.read_text(encoding="utf-8-sig").strip()
    if text.startswith("window.YTD."):
        marker = text.find("=")
        if marker < 0:
            raise ValueError(f"Malformed X archive JavaScript: {path}")
        text = text[marker + 1 :].strip()
    if text.endswith(";"):
        text = text[:-1].rstrip()
    return json.loads(text)


def _canonicalize(raw: dict) -> Post:
    text = html.unescape(str(raw.get("full_text") or raw.get("text") or "")).strip()
    created_raw = raw.get("created_at")
    if not created_raw:
        raise ValueError(f"tweet {raw.get('id', '<unknown>')} has no created_at")
    created_at = datetime.strptime(str(created_raw), _X_DATE)

    entities = raw.get("entities") or {}
    urls = tuple(
        str(item.get("expanded_url") or item.get("url"))
        for item in entities.get("urls", [])
        if item.get("expanded_url") or item.get("url")
    )
    hashtags = tuple(
        str(item.get("text"))
        for item in entities.get("hashtags", [])
        if item.get("text")
    )
    reply_status = _none_or_str(raw.get("in_reply_to_status_id") or raw.get("in_reply_to_status_id_str"))
    reply_user = _none_or_str(raw.get("in_reply_to_user_id") or raw.get("in_reply_to_user_id_str"))

    return Post(
        id=str(raw.get("id_str") or raw.get("id") or ""),
        created_at=created_at,
        text=text,
        conversation_id=_none_or_str(raw.get("conversation_id") or raw.get("conversation_id_str")),
        in_reply_to_status_id=reply_status,
        in_reply_to_user_id=reply_user,
        is_reply=reply_status is not None or reply_user is not None,
        urls=urls,
        hashtags=hashtags,
    )


def _is_url_only(text: str) -> bool:
    return not _URL_RE.sub("", text).strip()


def _none_or_str(value) -> str | None:
    return None if value is None else str(value)
