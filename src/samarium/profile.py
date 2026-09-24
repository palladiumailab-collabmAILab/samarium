"""Build an auditable persona profile from canonical posts."""

from __future__ import annotations

import re
from collections import Counter

from .models import CanonicalPost, PersonaProfile
from .text import character_ngrams, tokens

_PUNCTUATION = ("。", "、", "！", "？", "!", "?", "…", "〜")
_FIRST_PERSON = ("私", "僕", "俺", "自分", "わたし", "ぼく")
_EMOJI = re.compile("[\U0001F300-\U0001FAFF\u2600-\u27BF]")


def build_profile(posts: list[CanonicalPost], limit: int = 12) -> PersonaProfile:
    if not posts:
        raise ValueError("at least one canonical post is required")

    term_counts: Counter[str] = Counter()
    emoji_counts: Counter[str] = Counter()
    person_counts: Counter[str] = Counter()
    phrase_counts: Counter[str] = Counter()
    topic_counts: Counter[str] = Counter()
    punctuation_counts: Counter[str] = Counter()

    for post in posts:
        term_counts.update(tokens(post.text))
        emoji_counts.update(_EMOJI.findall(post.text))
        person_counts.update({word: post.text.count(word) for word in _FIRST_PERSON if word in post.text})
        phrase_counts.update(character_ngrams(post.text, 3))
        topic_counts.update(tag.casefold() for tag in post.hashtags)
        punctuation_counts.update({mark: post.text.count(mark) for mark in _PUNCTUATION if mark in post.text})

    character_count = sum(len(post.text) for post in posts) or 1
    punctuation = {mark: round(punctuation_counts[mark] / character_count, 4) for mark in _PUNCTUATION}
    repeated_phrases = tuple((text, count) for text, count in phrase_counts.most_common() if count > 1)[:limit]

    return PersonaProfile(
        post_count=len(posts),
        average_length=round(character_count / len(posts), 2),
        reply_ratio=round(sum(post.is_reply for post in posts) / len(posts), 4),
        frequent_terms=tuple(term_counts.most_common(limit)),
        punctuation=punctuation,
        emoji=tuple(emoji_counts.most_common(limit)),
        first_person=tuple(person_counts.most_common(limit)),
        typical_phrases=repeated_phrases,
        topics=tuple(topic_counts.most_common(limit)),
    )
