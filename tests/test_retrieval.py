from pathlib import Path

from samarium.retrieval import CharNgramRetriever
from samarium.x_archive import load_x_archive


FIXTURE = Path(__file__).parent / "fixtures" / "tweets.js"


def test_retriever_prefers_related_post() -> None:
    posts = load_x_archive(FIXTURE)
    retriever = CharNgramRetriever(posts)
    result = retriever.search("実装が動いた", k=2)
    assert result
    assert result[0].id == "101"
