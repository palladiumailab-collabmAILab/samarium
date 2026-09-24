from datetime import datetime, timezone
from unittest import TestCase

from samarium.models import CanonicalPost
from samarium.retrieval import LocalRetriever, _cosine


class RetrievalBoundaryTests(TestCase):
    def test_non_positive_limit_returns_empty(self) -> None:
        retriever = LocalRetriever([])
        self.assertEqual(retriever.search("anything", limit=0), [])
        self.assertEqual(retriever.search("anything", limit=-1), [])

    def test_cosine_handles_empty_vectors(self) -> None:
        self.assertEqual(_cosine({}, {"x": 1.0}), 0.0)
        self.assertEqual(_cosine({"x": 1.0}, {}), 0.0)

    def test_before_boundary_is_exclusive(self) -> None:
        boundary = datetime(2024, 1, 1, tzinfo=timezone.utc)
        posts = [
            CanonicalPost(
                id="1",
                text="coffee",
                created_at=boundary,
                is_reply=False,
                conversation_id=None,
            )
        ]
        result = LocalRetriever(posts).search("coffee", before=boundary)
        self.assertEqual(result, [])
