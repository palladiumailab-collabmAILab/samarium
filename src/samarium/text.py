"""Small deterministic text helpers with no external tokenizer dependency."""

from __future__ import annotations

import re

_TOKEN = re.compile(r"[A-Za-z0-9_]+|[ぁ-んァ-ヶ一-龠々ー]{2,}")
_URL = re.compile(r"https?://\S+", re.IGNORECASE)


def tokens(text: str) -> list[str]:
    cleaned = _URL.sub(" ", text.casefold())
    return _TOKEN.findall(cleaned)


def character_ngrams(text: str, size: int = 3) -> list[str]:
    cleaned = re.sub(r"\s+", "", _URL.sub("", text))
    return [cleaned[index : index + size] for index in range(max(0, len(cleaned) - size + 1))]


def retrieval_features(text: str) -> list[str]:
    """Combine word-like tokens and character features for Japanese retrieval."""
    word_features = [f"word:{token}" for token in tokens(text)]
    character_features = [f"char:{token}" for token in character_ngrams(text, 3)]
    return word_features + character_features
