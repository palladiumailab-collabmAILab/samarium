"""End-to-end orchestration without coupling to a concrete model provider."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from .archive import load_x_archive
from .llm import LLMProvider
from .models import CanonicalPost, LLMRequest, PersonaProfile
from .profile import build_profile
from .prompting import build_request
from .retrieval import LocalRetriever


@dataclass(frozen=True, slots=True)
class PersonaResult:
    posts: tuple[CanonicalPost, ...]
    profile: PersonaProfile
    examples: tuple[CanonicalPost, ...]
    request: LLMRequest
    output: str


class PersonaPipeline:
    def __init__(self, provider: LLMProvider, example_limit: int = 5) -> None:
        self._provider = provider
        self._example_limit = example_limit

    def run(
        self,
        archive_path: str | Path,
        query: str,
        *,
        before: datetime | None = None,
        exclude_ids: set[str] | None = None,
    ) -> PersonaResult:
        posts = load_x_archive(archive_path)
        if before is not None:
            profile_posts = [post for post in posts if post.created_at < before]
        else:
            profile_posts = posts
        profile = build_profile(profile_posts)
        examples = LocalRetriever(profile_posts).search(
            query,
            limit=self._example_limit,
            before=before,
            exclude_ids=exclude_ids,
        )
        request = build_request(query, profile, examples)
        return PersonaResult(
            posts=tuple(posts),
            profile=profile,
            examples=tuple(examples),
            request=request,
            output=self._provider.generate(request),
        )
