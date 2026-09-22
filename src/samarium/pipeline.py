from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from .llm import ChatLLM
from .models import PersonaProfile, Post
from .persona import build_persona_profile
from .prompting import build_system_prompt, build_user_prompt
from .retrieval import CharNgramRetriever, Retriever


@dataclass(slots=True)
class PersonaEngine:
    profile: PersonaProfile
    retriever: Retriever
    llm: ChatLLM

    @classmethod
    def from_posts(
        cls,
        posts: Sequence[Post],
        llm: ChatLLM,
        *,
        retriever: Retriever | None = None,
    ) -> "PersonaEngine":
        if not posts:
            raise ValueError("At least one post is required")
        profile = build_persona_profile(posts)
        return cls(
            profile=profile,
            retriever=retriever or CharNgramRetriever(posts),
            llm=llm,
        )

    def reply(self, query: str, *, k: int = 5) -> str:
        examples = self.retriever.search(query, k=k)
        return self.llm.generate(
            system=build_system_prompt(self.profile),
            user=build_user_prompt(query, examples),
        )
