from pathlib import Path

from samarium.llm import MockLLM
from samarium.pipeline import PersonaEngine
from samarium.x_archive import load_x_archive


FIXTURE = Path(__file__).parent / "fixtures" / "tweets.js"


def test_end_to_end_with_mock_llm() -> None:
    posts = load_x_archive(FIXTURE)
    llm = MockLLM(response="了解。小さく試す。")
    engine = PersonaEngine.from_posts(posts, llm)

    assert engine.reply("この実装どうする？", k=2) == "了解。小さく試す。"
    assert len(llm.calls) == 1
    call = llm.calls[0]
    assert "PERSONA PROFILE" in call["system"]
    assert "この実装" in call["user"]
    assert "Historical style examples" in call["user"]
