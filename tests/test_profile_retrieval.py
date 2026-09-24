from datetime import datetime, timezone
from pathlib import Path
from unittest import TestCase

from samarium.archive import load_x_archive
from samarium.profile import build_profile
from samarium.retrieval import LocalRetriever


FIXTURE = Path(__file__).parent / "fixtures" / "tweets.js"


class ProfileAndRetrievalTests(TestCase):
    def setUp(self) -> None:
        self.posts = load_x_archive(FIXTURE)

    def test_profile_captures_style_and_modes(self) -> None:
        profile = build_profile(self.posts)

        self.assertEqual(profile.post_count, 3)
        self.assertAlmostEqual(profile.reply_ratio, 1 / 3, places=4)
        self.assertIn(("僕", 2), profile.first_person)
        self.assertIn(("読書", 2), profile.topics)

    def test_retrieval_respects_holdout_and_exclusions(self) -> None:
        result = LocalRetriever(self.posts).search(
            "コーヒーと本",
            before=datetime(2024, 1, 3, tzinfo=timezone.utc),
            exclude_ids={"100"},
        )

        self.assertEqual([post.id for post in result], ["101"])

    def test_retrieval_uses_japanese_character_features(self) -> None:
        result = LocalRetriever(self.posts).search("週末のコーヒー", limit=1)

        self.assertEqual(result[0].id, "101")
