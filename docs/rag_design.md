# RAG全体アーキテクチャ設計（ハッカソン提出用）

## 概要
- RAGの本質は「検索精度」だけでなく「評価・運用設計」にある
- 本テンプレートは、思想・設計・APIインターフェースのみ公開
- 実装の細部（chunk設計・reranking・権威ルール等）は非公開

## レイヤ構成
1. RAG思想・設計（主役）
   - 図＋文章で説明
2. RAGインターフェース（API）
   - answer(question, retrieve_fn, k) の形のみ公開
3. RAG実装の中身
   - ブラックボックス化（非公開）

## アーキテクチャ図（例）

```
[User Question]
      ↓
[answer() API] ← retrieve_fn (外部注入)
      ↓
[内部RAGロジック（非公開）]
      ↓
[Answer + Docs + Metrics]
      ↓
[Evaluation (evaluate_public.py)]
      ↓
[Logs / Failure Tags]
      ↓
[改善判断（思想のみ公開）]
```
- 改善判断は基本的に **人（運用者）を想定**
- 将来的には **Agent による半自動改善も視野**

### 評価ループの全体像

      ┌───────────────┐
      │     User      │
      └───────┬───────┘
              ↓
        ┌──────────┐
        │   RAG    │
        │(answer)  │
        └──────┬───┘
               ↓
      ┌────────────────┐
      │   Evaluation   │
      │(must_include,  │
      │ hallucination) │
      └──────┬─────────┘
             ↓
      ┌────────────────┐
      │  Logs / Tags   │
      └──────┬─────────┘
             ↓
      ┌────────────────┐
      │ 改善判断（人） │
      │ or Agent       │
      └──────┬─────────┘
             ↓
      ┌────────────────┐
      │  RAG改善       │
      │(retriever /    │
      │ prompt / data) │
      └──────┬─────────┘
             └───────（ループ）──────┘

この図は、RAGの品質がどのように継続的に改善されるかを示している。

RAG → 評価 → ログ → 改善 → RAG

このサイクルを回すことで、RAGの品質を継続的に高める思想を体現している。

- 本テンプレートは、このループを「回せる形」にすることを目的とする  
- evaluate は **品質の“可視化装置”**  
- failure_tags は **改善の起点**  
- 改善判断は基本的に **人（運用者）を想定**  
- 将来的には **Agent による半自動改善も視野**

改善の主な対象は次の3つとする：
- 検索（retrieve_fn）：取得数、順位付け、文書粒度  
- データ（ingest）：不足・重複・古い情報  
- 生成（answer）：プロンプトやガードレール

```
## 本設計が最終的に出したいもの（Outputs）
本テンプレートでは、単なる回答ではなく「評価可能な出力」を重視する。
- Answer（回答）
- Docs（参照文書）
- Metrics（品質メトリクス）
- Failure Tags（失敗の種類）
- Suggested Actions（改善アクション）
これらを通じて、RAGの品質を評価・改善するための情報を提供する。
```

## ポイント
- RAGの「外形（API＋思想）」は公開
- RAGの「中身のロジック」は非公開
- evaluateは「思想＋簡易版コード」を公開

## 参考：APIインターフェース例
```python
def answer(question: str, retrieve_fn, k: int = 5, history=None):
    docs = retrieve_fn(question, k)
    return {
        "answer": "（簡易回答）",
        "docs": docs,
        "metrics": {}
    }
```

## RAG全体フロー概要
### 1. データ前処理・サニタイズ
- **主ファイル/関数**:
  - `scripts/preprocess_batch.py`
  - 入力データ（data/ 配下）を読み込み、不要情報削除・フォーマット統一
  - サニタイズ済データを `sanitized/` 配下に保存
### 2. データ登録（Ingest）
- **主ファイル/関数**:
  - `scripts/ingest_full.py`
  - `public/ingest_interface.py` の `ingest()` を呼び出し
  - `sanitized/` 配下のデータをベクトルストア（Chroma等）に登録
      - 登録メタ情報・ログを `work/ingest_runs/` 配下に保存
### 3. ベクトルストア初期化・接続
- **主ファイル/関数**:
  - `src/mycompany/vectorstore/init_vectorstore.py`
  - ベクトルストアクライアント（Chroma等）を初期化・接続
  - 環境変数や設定ファイルで接続情報を管理
### 4. Retriever準備
- **主ファイル/クラス**:
  - `src/mycompany/answer/answer.py`：Retrieverの初期化・選択
  - `SimpleRetriever`, `ChromaRetriever`（rag_core/business_rag.py, rag_core/shiso_rag.py など）
  - 環境変数RETRIEVER_BACKENDで切替
### 5. リクエスト送信（ユーザ質問受付）
- **主ファイル/関数**:
  - `ui/user/app.py`：ユーザUI（Streamlit）
  - `ui/e2e/app.py`：運用者UI
  - `evaluate.py`：CLI/バッチ評価
  - いずれも `src/mycompany/answer/answer.py` の `answer()` を呼び出し
### 6. オーケストレータ呼び出し
- **主ファイル/関数**:
  - `src/mycompany/answer/answer.py` の `answer()`
  - `apply_guardrail()`, `check_shiso()`（src/mycompany/guardrail.py）: 入力チェック
  - 回答モード判定（rag/general/guardrail等）
  - Retriever選択・検索呼び出し
### 7. Retriever検索
- **主ファイル/クラス/関数**:
  - `SimpleRetriever`, `ChromaRetriever`（rag_core/business_rag.py, rag_core/shiso_rag.py, rag_core/support_rag.py など）
  - `search()`, `retrieve()` メソッド：質問文のベクトル化・類似チャンク検索
  - 検索結果（チャンク＋メタ情報）を返却
### 8. 検索結果から回答生成
- **主ファイル/関数**:
  - `src/mycompany/answer/answer.py` の `answer()`
  - 検索結果＋設計思想・ガバナンスルール＋質問内容でプロンプト組立
  - LLMクライアント呼び出し（OpenAI API等、クライアント実装は別途）
  - 最終回答を整形し、UI/CLIに返却
- **ログ記録**: work/ingest_runs/ 配下や log/user_qa/ にqa_log等を保存

---
### 【全体フローまとめ】
1. scripts/preprocess_batch.py で data/ → sanitized/ へ前処理
2. scripts/ingest_full.py で sanitized/ → VectorStore へingest
3. UIやCLIから質問を受け、src/mycompany/answer/answer.py の answer() を呼び出し
4. answer() 内で Guardrailチェック・Retriever選択・検索・プロンプト組立・LLM呼び出し・回答返却
5. 検索・回答生成の詳細は rag_core/ 以下のRetrieverクラスや LLMクライアント実装に委譲
6. 各工程のログ・メタ情報は work/ingest_runs/ や log/user_qa/ に記録
---
各工程の詳細な実装は、上記ファイル・関数を参照してください。
