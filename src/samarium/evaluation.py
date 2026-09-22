from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from .models import Post
from .persona import build_persona_profile


@dataclass(frozen=True, slots=True)
class ChronologicalSplit:
    train: tuple[Post, ...]
    holdout: tuple[Post, ...]


def chronological_split(posts: Sequence[Post], *, holdout_ratio: float = 0.2) -> ChronologicalSplit:
    if len(posts) < 2:
        raise ValueError("At least two posts are required for a split")
    if not 0 < holdout_ratio < 1:
        raise ValueError("holdout_ratio must be between 0 and 1")
    ordered = sorted(posts, key=lambda post: (post.created_at, post.id))
    holdout_count = max(1, round(len(ordered) * holdout_ratio))
    holdout_count = min(holdout_count, len(ordered) - 1)
    cut = len(ordered) - holdout_count
    return ChronologicalSplit(tuple(ordered[:cut]), tuple(ordered[cut:]))


def style_distance(reference: Sequence[Post], generated_texts: Sequence[str]) -> float:
    """Small, interpretable baseline distance; lower is better.

    Uses coarse style statistics only. Semantic/persona quality still requires
    held-out generation tests and human A/B evaluation.
    """
    if not reference:
        raise ValueError("reference must not be empty")
    if not generated_texts:
        raise ValueError("generated_texts must not be empty")
    reference_profile = build_persona_profile(reference)
    generated_posts = [
        Post(
            id=f"generated-{index}",
            created_at=reference[0].created_at,
            text=text,
        )
        for index, text in enumerate(generated_texts)
    ]
    generated_profile = build_persona_profile(generated_posts)

    terms = [
        _relative_gap(reference_profile.avg_chars, generated_profile.avg_chars),
        abs(reference_profile.newline_ratio - generated_profile.newline_ratio),
        abs(reference_profile.question_ratio - generated_profile.question_ratio),
        abs(reference_profile.exclamation_ratio - generated_profile.exclamation_ratio),
    ]
    return sum(terms) / len(terms)


def _relative_gap(left: float, right: float) -> float:
    scale = max(abs(left), 1.0)
    return abs(left - right) / scale
