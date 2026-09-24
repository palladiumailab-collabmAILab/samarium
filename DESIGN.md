# Design

## Purpose

X archiveからpersona生成に必要な再現可能なcontextを構築し、raw postを直接fine-tuningする前に、local retrievalでどこまでpersona再現できるかを検証する。

## Design principles

- **local-first。** archive、profile、retrieval index、生成outputはローカルで扱う。
- **canonical post modelを先に作る。** providerやfine-tuning方式に依存する前に、入力を正規化する。
- **deterministic baseline first。** profile統計とTF-IDF retrievalを基準線にし、その上でLLMや将来のLoRA/SFTを比較する。
- **temporal leakageを避ける。** optional cutoffとID exclusionで未来情報や同一postの混入を防ぐ。
- **provider-neutral。** pipelineの中核を特定LLM APIへ結合しない。
- **fine-tuningは実証後。** chronological holdoutとblind human evaluationでbaseline超過が確認されるまでMVPに含めない。
- **本人の実発言と生成文を混同しない。**

## Non-goals

- MVP段階でraw postを直接fine-tuningすること。
- Xへ自動投稿すること。
- private archiveや生成profileをGitへ保存すること。

## Architecture intent

ingestion、canonical model、profile、retrieval、prompting、LLM adapter、orchestrationを分離し、将来のLoRA/SFTがingestion contractを壊さず追加できる構造にする。
