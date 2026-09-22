from pathlib import Path

from samarium.persona import build_persona_profile
from samarium.x_archive import load_x_archive


FIXTURE = Path(__file__).parent / "fixtures" / "tweets.js"


def test_profile_has_expected_coarse_statistics() -> None:
    posts = load_x_archive(FIXTURE)
    profile = build_persona_profile(posts)
    assert profile.post_count == 4
    assert profile.reply_ratio == 0.25
    assert profile.question_ratio == 0.25
    assert profile.avg_chars > 0
    assert profile.top_ngrams
