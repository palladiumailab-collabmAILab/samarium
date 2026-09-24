from pathlib import Path
from unittest import TestCase

from samarium.llm import MockLLM
from samarium.pipeline import PersonaPipeline


FIXTURE = Path(__file__).parent / "fixtures" / "tweets.js"


class PipelineTests(TestCase):
    def test_mock_archive_runs_end_to_end(self) -> None:
        result = PersonaPipeline(MockLLM(), example_limit=2).run(
            FIXTURE,
            "週末は何をする？",
        )

        self.assertEqual(result.profile.post_count, 3)
        self.assertEqual(len(result.examples), 2)
        self.assertEqual(result.request.metadata["example_ids"], [post.id for post in result.examples])
        self.assertIn("本人であると主張せず", result.request.system_prompt)
        self.assertEqual(result.output, "[mock persona: 2 examples] 週末は何をする？")
