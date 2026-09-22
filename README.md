# samarium

X（Twitter）の**所有アカウントの公式アーカイブ**から、文体・語彙・応答傾向を再現するpersona LLMの実験基盤です。

## 設計

初期MVPではraw投稿を直接fine-tuningしません。

1. X archive -> canonical posts
2. canonical posts -> persona profile
3. 入力に近い過去投稿をretrieval
4. profile + retrieved examples + inputをbase LLMへ渡す
5. 時系列holdout + blind A/Bで評価
6. baselineを上回れる場合のみLoRA/QLoRA SFTを追加

この順序にする理由は、Xの短文ログでは「文体学習」と「投稿内容の暗記」が混ざりやすいためです。retrieval-firstなら、実データを変更せずにprompt・検索器・LLMを独立に比較できます。

## 現在のMVP

- X `tweets.js` / JSON parser
- canonical JSONL
- persona profile builder
- 日本語でも依存ゼロで動く文字n-gram retriever
- prompt builder
- LLM provider protocol
- `MockLLM`
- 時系列split / coarse style distance
- mock X archiveによるE2E test

文字n-gram retrieverは**テスト可能なbaseline**です。実運用では`Retriever` interfaceのままembedding retrievalへ差し替えることを想定しています。

## Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pytest
```

## X archiveの投入

X公式アーカイブを展開し、Git管理対象外の`data/private/`に置きます。

```bash
samarium ingest data/private/x-archive --output data/private/posts.jsonl
samarium inspect data/private/posts.jsonl
```

`data/private/`は`.gitignore`されています。実アーカイブや生成したprivate JSONLをコミットしないでください。

## 次段階

1. embedding retrieverを追加し、文字n-gram baselineと比較
2. 時系列holdoutでgeneration setを固定
3. 本人によるblind A/B評価器を追加
4. 十分な学習例がある場合のみLoRA/QLoRA SFT
5. fine-tuned modelがretrieval-first baselineを上回るか評価

Issue #1 に設計判断と完了条件を記載しています。
