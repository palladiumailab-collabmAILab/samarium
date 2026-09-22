from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from .persona import build_persona_profile
from .x_archive import load_x_archive, read_jsonl, write_jsonl


def main() -> None:
    parser = argparse.ArgumentParser(prog="samarium")
    sub = parser.add_subparsers(dest="command", required=True)

    ingest = sub.add_parser("ingest", help="Convert an extracted X archive to canonical JSONL")
    ingest.add_argument("archive", type=Path)
    ingest.add_argument("--output", type=Path, default=Path("data/private/posts.jsonl"))

    inspect = sub.add_parser("inspect", help="Print a persona profile from archive or JSONL")
    inspect.add_argument("source", type=Path)

    args = parser.parse_args()
    if args.command == "ingest":
        posts = load_x_archive(args.archive)
        write_jsonl(posts, args.output)
        print(f"wrote {len(posts)} posts to {args.output}")
        return

    posts = read_jsonl(args.source) if args.source.suffix == ".jsonl" else load_x_archive(args.source)
    profile = build_persona_profile(posts)
    print(json.dumps(asdict(profile), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
