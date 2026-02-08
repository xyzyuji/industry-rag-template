## 🚀 Live Demo (GCP Cloud Run)

Public版の answer() は Cloud Run にデプロイできます。

### API例

POST /answer
```
{
	"question": "RAGとは？",
	"k": 3
}
```

POST /evaluate
```
{
	"question": "RAGとは？",
	"must_include": ["keyword1", "keyword2"]
}
```

※ 内部は Public Edition の簡易スタブ実装です。

Cloud Run デプロイ例:

```
gcloud run deploy rag-public \
	--source . \
	--region asia-northeast1 \
	--allow-unauthenticated
```

（URLは本番デプロイ後に記載）



# RAG Evaluation Template（Hackathon Public Edition）

## 🎯 Overview

多くの RAG システムは「動くこと」に注力しています。
しかし、本番運用では次の問題が必ず起きます。

* どの回答が“失敗”かを定義できない
* 改善が属人化する
* ログはあるが、判断に使えない

本リポジトリは、**RAG を“運用可能なシステム”にするための評価設計テンプレート**です。
「RAG の本質は評価・運用設計」という思想を主役に、**最低限の動くデモと設計ドキュメントをセットで提供**します。

このリポジトリは、RAG / Agent サービスの評価・運用思想を体験できる「評価テンプレート（簡易版）」です。

---

## 🎯 想定ユーザー

* RAG を PoC から本番に持っていきたいチーム
* 評価基準を作りたい ML / LLM エンジニア
* RAG の品質管理を標準化したいリードエンジニア

---

## ✨ 特徴

* RAG の**評価・運用設計思想を重視**
* 最低限の動く評価デモ（コード＋思想）
* `must_include` 判定・hallucination 判定など、基本的な評価ロジックのみ公開
* 本番用の詳細ロジック・閾値設計・改善判断は非公開

---

## 🧪 Public Edition の位置づけ（重要）

本リポジトリの Public Edition は：

- RAG の「評価・運用思想」を伝えることが主目的
- 実装はあえて“簡易スタブ”
- 本番用の検索・埋め込み・評価ロジックは非公開（private版で管理）

ローカルデモ：
- `public/local_ui_demo.py`

APIデモ：
- `public_api.py`（FastAPI）

---

## 📁 リポジトリ構成

```
docs/
	├── evaluation_design.md   # 評価思想・設計の説明
	└── rag_design.md          # RAG 全体アーキテクチャ・API設計

public/
	├── answer_interface.py    # RAG の API インターフェース（外形のみ公開）
	├── ingest_interface.py    # データ登録 API（外形のみ公開）
	├── local_ui_demo.py       # ローカル評価デモUI
	├── evaluate_core.py       # 評価ロジック（本質）
	└── evaluate_cli.py        # CLI 実行用ラッパー

public_api.py               # FastAPI（評価デモ用API）
```

---

## 🚀 使い方

1. `public/evaluate_cli.py` を実行
2. サンプル設問（`qid, type, must_include, ideal_answer`）に対し `answer()` を呼び出し
3. 以下を含む評価結果を JSON で出力：

	 * `must_include_ok`
	 * `hallucination`
	 * `failure_tags`
	 * `suggested_action`

---

## 🧪 Cloud Run デモフロー（/answer → /evaluate）

本テンプレートでは、RAG の回答生成だけでなく、**回答を機械的に評価するところまで**を一連のフローとしてデモできます。

1. 質問 → 回答生成（/answer）

	 ```http
	 POST /answer
	 Content-Type: application/json

	 {
		 "question": "RAGとは何ですか？",
		 "k": 3
	 }
	 ```

	 レスポンス例：

	 ```json
	 {
		 "answer": "RAG（Retrieval-Augmented Generation）は、外部知識を検索してから回答を生成する手法です。",
		 "docs": [
			 {"id": "doc_1", "text": "RAGは外部知識を検索して活用する..."}
		 ],
		 "metrics": {"status": "ok"}
	 }
	 ```

2. 回答 → 品質評価（/evaluate）

	 ```http
	 POST /evaluate
	 Content-Type: application/json

	 {
		 "question": "RAGとは何ですか？",
		 "must_include": ["外部知識", "検索"]
	 }
	 ```

	 レスポンス例：

	 ```json
	 {
		 "generated": "RAG（Retrieval-Augmented Generation）は、外部知識を検索してから回答を生成する手法です。",
		 "must_include": {
			 "all_ok": true,
			 "detail": {
				 "外部知識": true,
				 "検索": true
			 }
		 },
		 "hallucination": false
	 }
	 ```

このように、

- `/answer` : RAG による回答生成
- `/evaluate` : その回答に対する **必須キーワード（must_include）** と **hallucination の簡易判定**

までを API として分離しつつ、評価・運用の流れをデモできる構成になっています。

---

## 🔐 公開方針・注意

* ベクトルストア（Chroma 等）の設計・パラメータ・運用ノウハウは資産のため**非公開**
* public 版は **API インターフェース（retrieve_fn, ingest）のみ公開**
* 内部ロジックはブラックボックスまたはダミー実装
* 本番用のベクトルストア・ingest・評価ロジックは `private/` または別リポジトリで管理し、必要に応じて連携可能
* データ登録の流れや API インターフェースは公開するが、内部処理は簡易化・抽象化
* サンプルデータを返すスタブやダミー関数を用意し、実装の詳細は非公開

---

## 🔁 評価 → 改善ループ（思想）

本テンプレートは、次のループを“回せる形”にすることを目的としています。

```
RAG → Evaluation → Logs / Tags → 改善判断 → RAG
```

* `evaluate` は **品質の“可視化装置”**
* `failure_tags` は **改善の起点**
* 改善判断は基本的に **人（運用者）を想定**
* 将来的には **Agent による半自動改善も視野**

主な改善対象：

* **検索（retrieve_fn）**：取得数、順位付け、文書粒度
* **データ（ingest）**：不足・重複・古い情報
* **生成（answer）**：プロンプトやガードレール

---

## ✅ このテンプレートが解決すること（例）

❌ よくある状況：

* RAG の回答は出るが、品質が測れない
* どこが悪いのか分からない
* 改善の判断が属人化

✅ 本テンプレート：

* 設問ベースで評価（`qid, must_include, ideal_answer`）
* 自動ラベリング（`must_include / hallucination`）
* ログ蓄積 → 改善判断の思想を提供
* `failure_tags`・`suggested_action` で「次のアクション」まで示唆

👉 **評価 → ログ → 改善 → RAG のループを回せる設計を実現します。**

---


## 📌 バージョン構成と今後の拡張（Roadmap）

- **v1（現状）**：評価・運用フレーム（技術に依存しない設計・API・評価ループが主役）
- **v2（拡張）**：検索部分をGraphRAGやLangGraph等の先進技術に差し替え・拡張可能な構成へ

このように「評価・運用思想（フレーム）」と「技術実装（検索/GraphRAG等）」を分離し、将来の技術進化にも柔軟に対応できる設計です。

---

### その他拡張案

* 再ランキング（reranking）
* 権威ルール（最新版優先 / 全社規程優先）
* clarification（聞き返し）Agent
* アクセス制御（権限ベースの検索）
* 半自動改善 Agent

---

## 📄 License

MIT License
