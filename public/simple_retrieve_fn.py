"""
リアルRAG風の簡易retrieve_fn（public用）
- sample_docs.txt から単純なキーワード検索
"""
def simple_retrieve_fn(question, k):
    docs = [
        "RAGは検索と生成を組み合わせた技術です。",
        "評価と運用設計がRAGの本質です。",
        "Cloud RunでRAGを運用できます。"
    ]
    return [d for d in docs if any(w in d for w in question.split())][:k]
