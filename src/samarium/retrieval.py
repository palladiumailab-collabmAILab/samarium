"""A compact in-memory TF-IDF retriever for persona examples."""

from __future__ import annotations

import math
from collections import Counter
from datetime import datetime

from .models import CanonicalPost
from .text import retrieval_features


class LocalRetriever:
    def __init__(self, posts: list[CanonicalPost]) -> None:
        self._posts = tuple(posts)
        self._documents = [Counter(retrieval_features(post.text)) for post in posts]
        document_frequency: Counter[str] = Counter()
        for document in self._documents:
            document_frequency.update(document.keys())
        count = len(posts)
        self._idf = {
            term: math.log((1 + count) / (1 + frequency)) + 1
            for term, frequency in document_frequency.items()
        }

    def search(
        self,
        query: str,
        *,
        limit: int = 5,
        before: datetime | None = None,
        exclude_ids: set[str] | None = None,
    ) -> list[CanonicalPost]:
        if limit < 1:
            return []
        query_vector = self._weighted(Counter(retrieval_features(query)))
        excluded = exclude_ids or set()
        scored: list[tuple[float, CanonicalPost]] = []

        for post, document in zip(self._posts, self._documents, strict=True):
            if post.id in excluded or (before is not None and post.created_at >= before):
                continue
            score = _cosine(query_vector, self._weighted(document))
            scored.append((score, post))

        scored.sort(key=lambda item: (item[0], item[1].created_at, item[1].id), reverse=True)
        return [post for _, post in scored[:limit]]

    def _weighted(self, counts: Counter[str]) -> dict[str, float]:
        return {term: count * self._idf.get(term, 1.0) for term, count in counts.items()}


def _cosine(left: dict[str, float], right: dict[str, float]) -> float:
    if not left or not right:
        return 0.0
    dot = sum(value * right.get(term, 0.0) for term, value in left.items())
    left_norm = math.sqrt(sum(value * value for value in left.values()))
    right_norm = math.sqrt(sum(value * value for value in right.values()))
    return dot / (left_norm * right_norm) if left_norm and right_norm else 0.0
