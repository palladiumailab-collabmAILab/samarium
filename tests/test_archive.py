from pathlib import Path
from unittest import TestCase

import json
import tempfile

from samarium.archive import load_x_archive, write_canonical_jsonl


FIXTURE = Path(__file__).parent / "fixtures" / "tweets.js"


class ArchiveTests(TestCase):
    def test_loads_canonical_posts_and_filters_noise(self) -> None:
        posts = load_x_archive(FIXTURE)

        self.assertEqual([post.id for post in posts], ["100", "101", "102"])
        self.assertTrue(posts[2].is_reply)
        self.assertEqual(posts[0].hashtags, ("読書",))
        self.assertIsNotNone(posts[0].created_at.tzinfo)
        self.assertEqual(posts[0].to_dict()["id"], "100")

    def test_writes_canonical_jsonl(self) -> None:
        posts = load_x_archive(FIXTURE)
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "nested" / "posts.jsonl"
            write_canonical_jsonl(posts, output)
            records = [json.loads(line) for line in output.read_text(encoding="utf-8").splitlines()]

        self.assertEqual([record["id"] for record in records], ["100", "101", "102"])
        self.assertEqual(records[0]["hashtags"], ["読書"])
