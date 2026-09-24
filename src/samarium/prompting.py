"""Render provider-neutral prompts from a profile and retrieved examples."""

from __future__ import annotations

import json
from dataclasses import asdict

from .models import CanonicalPost, LLMRequest, PersonaProfile


def build_request(
    query: str,
    profile: PersonaProfile,
    examples: list[CanonicalPost],
) -> LLMRequest:
    profile_json = json.dumps(asdict(profile), ensure_ascii=False, sort_keys=True)
    rendered_examples = "\n".join(
        f"- [{post.created_at.date().isoformat()} / {'reply' if post.is_reply else 'post'}] {post.text}"
        for post in examples
    ) or "- (該当例なし)"
    system = (
        "あなたは過去投稿から抽出した文体上の特徴を参考に文章案を作る支援モデルです。\n"
        "投稿者本人であると主張せず、過去投稿を現在の事実として断定しないでください。\n"
        "例文の固有内容をコピーせず、語調・長さ・句読点・応答モードだけを参考にしてください。\n"
        f"Persona profile (statistics):\n{profile_json}\n"
        f"Retrieved style examples:\n{rendered_examples}"
    )
    return LLMRequest(
        system_prompt=system,
        user_prompt=query,
        metadata={"example_ids": [post.id for post in examples], "profile_posts": profile.post_count},
    )
