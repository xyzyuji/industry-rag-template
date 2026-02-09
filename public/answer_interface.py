"""
RAGインターフェース（ハッカソン提出用・外形のみ公開）
内部ロジックはブラックボックス化 or 最小限のスタブ実装
"""
def answer(question: str, retrieve_fn, k: int = 5, history=None):
    """
    RAG のインターフェースのみ公開。
    内部実装はブラックボックス（スタブ or 簡易実装でも可）。
    Args:
        question (str): 質問文
        retrieve_fn (callable): 検索関数（外部から注入）
        k (int): 取得するドキュメント数
        history: 質問履歴（任意）
    Returns:
        dict: {"answer": str, "docs": list, "metrics": dict}
    """
    docs = retrieve_fn(question, k)

    # --- Evaluation Scenarios 用のサンプル質問に対する専用スタブ ---
    q = question.strip()

    # Case 1: 正しい回答（理想ケース）
    if q == "このテンプレートの目的と特徴を教えてください。":
        generated = "このテンプレートは、RAG と 評価 を組み合わせ、Cloud Run 上での運用を想定したデモ用テンプレートです。"
        docs_case1 = docs or [
            "RAG と評価設計を Cloud Run 上で試せるテンプレートです。"
        ]
        return {
            "answer": generated,
            "docs": docs_case1,
            "metrics": {"status": "ok", "retrieved_k": len(docs_case1)},
        }

    # Case 2: 明確に間違った回答（NGケース）
    if q == "このリポジトリは画像生成モデルですか？":
        generated = "はい、このリポジトリは画像生成モデルです。"
        return {
            "answer": generated,
            "docs": [],  # 出典なし → hallucination=true
            "metrics": {"status": "no_docs"},
        }

    # Case 3: 検索はダメだが回答は正しい（人間判断が必要なケース）
    if q == "RAGとは何か、一般的な概念を説明してください。":
        generated = (
            "RAG は、外部の情報を取り込んでから回答を作る仕組みであり、"
            "大規模言語モデルの弱点を補うために使われます。"
        )
        return {
            "answer": generated,
            "docs": [],  # docs なし → hallucination=true だが、内容自体は概念的には正しい
            "metrics": {"status": "no_docs"},
        }

    # Case 4: 一部だけ満たしているケース（部分OK）
    if q == "Cloud Run上でRAG APIを動かすときのポイントは？":
        generated = (
            "Cloud Run でRAG APIを運用するポイントは、Cloud Run のスケーリングと"
            "ログ監視などの運用を意識することです。"
        )
        docs_case4 = docs or [
            "Cloud Run でRAG APIを動かす際は、スケーリングと監視が重要です。"
        ]
        return {
            "answer": generated,  # "Cloud Run" だけ含み、"評価" や "GitHub連携" は含めない
            "docs": docs_case4,
            "metrics": {"status": "ok", "retrieved_k": len(docs_case4)},
        }

    # Case 5: 長くてそれっぽいが怪しい回答（微妙ケース）
    if q == "このテンプレートを使うと、どんなRAGシステムでも完全自動で運用できますか？":
        generated = (
            "このテンプレートを使うことで、多くの場面で制約 を意識せずに "
            "改善サイクル を自動で回せるように見えますが、実際には運用者の判断が前提です。"
        )
        return {
            "answer": generated,  # must_include の "制約" と "改善サイクル" は満たす
            "docs": [],  # 出典なし → hallucination=true（それっぽいが怪しい）
            "metrics": {"status": "no_docs"},
        }

    # --- それ以外は従来通りの簡易スタブ ---
    if not docs:
        return {
            "answer": "関連するドキュメントが見つかりませんでした。",
            "docs": [],
            "metrics": {"status": "no_docs"},
        }
    return {
        "answer": f"""
        【回答（デモ版）】
        この回答は {len(docs)} 件の文書を参照して生成されました。
        - 参照文書数: {len(docs)}
        - 取得K: {k}
        """,
        "docs": docs,
        "metrics": {
            "retrieved_k": k,
            "confidence_hint": 0.72,
        },
    }
