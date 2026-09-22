from __future__ import annotations

import re
import statistics
from collections import Counter
from typing import Iterable

from .models import PersonaProfile, Post

_URL_RE = re.compile(r"https?://\S+")
_SPACE_RE = re.compile(r"[ \t]+")


def build_persona_profile(posts: Iterable[Post], *, max_ngrams: int = 12) -> PersonaProfile:
    posts = list(posts)
    if not posts:
        raise ValueError("At least one post is required")

    texts = [_style_text(post.text) for post in posts]
    lengths = [len(text) for text in texts]
    ngrams = Counter[str]()
    hashtags = Counter[str]()

    for post, text in zip(posts, texts, strict=True):
        ngrams.update(_char_ngrams(text))
        hashtags.update(tag.casefold() for tag in post.hashtags)

    return PersonaProfile(
        post_count=len(posts),
        reply_ratio=sum(post.is_reply for post in posts) / len(posts),
        avg_chars=sum(lengths) / len(lengths),
        median_chars=float(statistics.median(lengths)),
        newline_ratio=sum("\n" in text for text in texts) / len(texts),
        question_ratio=sum(("?" in text or "？" in text) for text in texts) / len(texts),
        exclamation_ratio=sum(("!" in text or "！" in text) for text in texts) / len(texts),
        top_ngrams=tuple(gram for gram, _ in ngrams.most_common(max_ngrams)),
        top_hashtags=tuple(tag for tag, _ in hashtags.most_common(8)),
    )


def _style_text(text: str) -> str:
    text = _URL_RE.sub("", text)
    lines = [_SPACE_RE.sub(" ", line).strip() for line in text.splitlines()]
    return "\n".join(line for line in lines if line)


def _char_ngrams(text: str) -> list[str]:
    compact = re.sub(r"\s+", "", text)
    grams: list[str] = []
    for n in (2, 3):
        grams.extend(compact[i : i + n] for i in range(max(0, len(compact) - n + 1)))
    return grams
