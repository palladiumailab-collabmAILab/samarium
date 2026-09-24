# samarium

`samarium` builds a reproducible persona-generation request from an exported X
archive. The MVP deliberately keeps factual memory in local retrieval instead
of fine-tuning on raw posts.

The pipeline is local-first:

1. parse `tweets.js` into a canonical post model;
2. remove retweets, URL-only posts, duplicates, and obvious automated posts;
3. build a statistical persona profile;
4. retrieve related historical examples without crossing an optional time
   cutoff;
5. build a provider-neutral LLM request;
6. exercise the complete flow with `MockLLM`.

No real archive, generated profile, or local output belongs in Git.

## Quick start with mock data

```bash
python -m samarium.cli tests/fixtures/tweets.js "週末は何をする？"
```

Pass `--jsonl data/output/posts.jsonl` to write the normalized records. For a
real archive, keep that output in an ignored private/output directory.

When running from a checkout without installing the package, set
`PYTHONPATH=src` (PowerShell: `$env:PYTHONPATH = "src"`).

## Validation

The canonical validation path is Docker:

```bash
docker compose build test
docker compose run --rm test
```

The tests use `unittest` assertions and can also run without installing host
dependencies:

```bash
python -m unittest discover -s tests -v
```

## Using a real X archive

1. Download the official archive from X.
2. Copy `data/twitter-archive/data/tweets.js` to
   `data/private/tweets.js`. The whole `data/private/` directory is ignored.
3. Parse it locally with `samarium.archive.load_x_archive` or pass it to the
   CLI shown above.

Do not commit raw archives, profiles derived from them, prompt dumps, or model
outputs. Review canonical posts before use and remove personal data that is not
needed for the intended persona. The MVP does not post to X and generated text
should not be represented as a real statement by the archive owner.

## Package boundaries

- `archive`: X export parsing, normalization, and filtering
- `models`: canonical data and provider-neutral request types
- `profile`: deterministic style/topic statistics
- `retrieval`: local TF-IDF example retrieval with time/ID exclusions
- `prompting`: profile and example rendering
- `llm`: provider protocol and deterministic mock
- `pipeline`: orchestration only; future LoRA/SFT code can consume canonical
  posts and evaluation splits without changing ingestion or retrieval

Fine-tuning is intentionally outside the MVP. It should be considered only
after a chronological holdout and blind human evaluation show an improvement
over this baseline.
