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
    # “それっぽい”振る舞い（半スタブ）
    if not docs:
        return {
            "answer": "関連するドキュメントが見つかりませんでした。",
            "docs": [],
            "metrics": {"status": "no_docs"}
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
            "confidence_hint": 0.72
        }
    }
