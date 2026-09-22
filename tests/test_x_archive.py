from pathlib import Path

from samarium.x_archive import load_x_archive, read_jsonl, write_jsonl


FIXTURE = Path(__file__).parent / "fixtures" / "tweets.js"


def test_load_x_archive_parses_and_filters_retweets() -> None:
    posts = load_x_archive(FIXTURE)
    assert [post.id for post in posts] == ["100", "101", "102", "103"]
    assert posts[-1].is_reply is True
    assert posts[0].hashtags == ("作業",)


def test_jsonl_round_trip(tmp_path: Path) -> None:
    posts = load_x_archive(FIXTURE)
    path = tmp_path / "posts.jsonl"
    write_jsonl(posts, path)
    assert read_jsonl(path) == posts


def test_archive_directory_ignores_unrelated_tweet_files(tmp_path: Path) -> None:
    archive = tmp_path / "data"
    archive.mkdir()
    (archive / "tweets.js").write_text(FIXTURE.read_text(encoding="utf-8"), encoding="utf-8")
    (archive / "deleted-tweets.js").write_text("window.YTD.deleted_tweets.part0 = []", encoding="utf-8")
    assert len(load_x_archive(tmp_path)) == 4
