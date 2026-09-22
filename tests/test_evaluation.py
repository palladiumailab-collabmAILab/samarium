from pathlib import Path

from samarium.evaluation import chronological_split, style_distance
from samarium.x_archive import load_x_archive


FIXTURE = Path(__file__).parent / "fixtures" / "tweets.js"


def test_chronological_split_keeps_future_posts_in_holdout() -> None:
    posts = load_x_archive(FIXTURE)
    split = chronological_split(posts, holdout_ratio=0.25)
    assert len(split.train) == 3
    assert [post.id for post in split.holdout] == ["103"]
    assert split.train[-1].created_at < split.holdout[0].created_at


def test_style_distance_is_zero_for_same_texts() -> None:
    posts = load_x_archive(FIXTURE)
    distance = style_distance(posts, [post.text for post in posts])
    assert distance == 0.0
