from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass, field
from typing import Protocol, Sequence

from .models import Post


class Retriever(Protocol):
    def search(self, query: str, *, k: int = 5) -> list[Post]: ...


@dataclass(slots=True)
class CharNgramRetriever:
    """Dependency-free Japanese-friendly retrieval baseline.

    This is intentionally simple. Replace it with embedding retrieval for real
    deployments while keeping the same ``Retriever`` interface.
    """

    posts: Sequence[Post]
    _vectors: tuple[Counter[str], ...] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self.posts = tuple(self.posts)
        self._vectors = tuple(_features(post.text) for post in self.posts)

    def search(self, query: str, *, k: int = 5) -> list[Post]:
        if k <= 0:
            return []
        query_vector = _features(query)
        scored = [
            (_cosine(query_vector, vector), index, post)
            for index, (post, vector) in enumerate(zip(self.posts, self._vectors, strict=True))
        ]
        scored.sort(key=lambda row: (row[0], row[1]), reverse=True)
        return [post for score, _, post in scored[:k] if score > 0]


def _features(text: str) -> Counter[str]:
    normalized = re.sub(r"\s+", "", text.casefold())
    features: Counter[str] = Counter()
    for n in (2, 3):
        for i in range(max(0, len(normalized) - n + 1)):
            features[f"c{n}:{normalized[i:i+n]}"] += 1
    for word in re.findall(r"[a-z0-9_+-]{2,}", text.casefold()):
        features[f"w:{word}"] += 2
    return features


def _cosine(left: Counter[str], right: Counter[str]) -> float:
    if not left or not right:
        return 0.0
    dot = sum(value * right.get(key, 0) for key, value in left.items())
    if dot == 0:
        return 0.0
    left_norm = math.sqrt(sum(value * value for value in left.values()))
    right_norm = math.sqrt(sum(value * value for value in right.values()))
    return dot / (left_norm * right_norm)
