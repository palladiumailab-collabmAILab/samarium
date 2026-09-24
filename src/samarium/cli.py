"""Minimal offline CLI for validating an archive and request flow."""

from __future__ import annotations

import argparse
from pathlib import Path

from .archive import write_canonical_jsonl
from .llm import MockLLM
from .pipeline import PersonaPipeline


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", help="path to X tweets.js")
    parser.add_argument("query", help="text to answer in the extracted style")
    parser.add_argument(
        "--jsonl",
        type=Path,
        help="optional path for canonical JSONL (keep real-data output outside Git)",
    )
    args = parser.parse_args()
    result = PersonaPipeline(MockLLM()).run(args.archive, args.query)
    if args.jsonl:
        write_canonical_jsonl(result.posts, args.jsonl)
    print(result.output)


if __name__ == "__main__":
    main()
