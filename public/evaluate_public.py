"""
Hackathon提出用 RAG評価デモ（簡易版・Public Edition）

方針：
- must_include 判定
- hallucination 判定（出典の有無）
- ダミー類似度スコア
- failure_tags と suggested_action（思想のデモ）
- 本番用の詳細ロジックは非公開

★評価は“点数づけ”ではなく“失敗の類型化”を主眼とする
"""


import json

# ==============================
# ====== ダミー answer ======
# ==============================
def answer(query: str):
    """
    Public版のダミー回答生成（本番はLLM/Agentを呼ぶ）
    """
    if "RAG" in query:
        return {
            "generated": "RAGは検索と生成を組み合わせた技術です。keyword1 keyword2 を含みます。",
            "sources": ["source_doc.txt"]
        }
    elif "Cloud" in query:
        return {
            "generated": "Cloud RunでRAGを運用できます。",
            "sources": []  # あえて出典なし（hallucination デモ）
        }
    else:
        return {
            "generated": "これはサンプル回答です。",
            "sources": []
        }

# ==============================
# ====== 評価ロジック（簡易）=====
# ==============================
def check_must_include(generated: str, must_include: list) -> bool:
    """must_include の全語が含まれているか（簡易版）"""
    return all(k in generated for k in must_include)

def check_hallucination(sources: list) -> bool:
    """出典が空なら hallucination とみなす（簡易版）"""
    return len(sources) == 0

def dummy_similarity(generated: str, ideal: str) -> float:
    """
    Public版のダミー類似度。
    本番では埋め込み類似度などを使用（非公開）。
    """
    return 0.42

# ==============================
# ====== 評価設問（サンプル）=====
# ==============================
questions = [
    {
        "qid": "q1",
        "type": "rag",
        "must_include": ["keyword1", "keyword2"],
        "ideal_answer": "keyword1とkeyword2を含む回答"
    },
    {
        "qid": "q2",
        "type": "rag",
        "must_include": ["Cloud", "運用"],
        "ideal_answer": "CloudでRAGを運用できる説明"
    },
    {
        "qid": "q3",
        "type": "rag",
        "must_include": ["example"],
        "ideal_answer": "exampleを含む説明"
    }
]

# ==============================
# ====== 評価実行 ======
# ==============================
results = []

for q in questions:
    res = answer(q["qid"])

    must_include_ok = check_must_include(res["generated"], q["must_include"])
    hallucination = check_hallucination(res["sources"])
    similarity = dummy_similarity(res["generated"], q["ideal_answer"])

    failure_tags = []
    if not must_include_ok:
        failure_tags.append("missing_must_include")
    if hallucination:
        failure_tags.append("hallucination")

    suggested_action = "要調査" if failure_tags else "OK"

    results.append({
        "qid": q["qid"],
        "must_include_ok": must_include_ok,
        "hallucination": hallucination,
        "similarity": similarity,
        "failure_tags": failure_tags,
        "suggested_action": suggested_action,
        "generated": res["generated"],
        "sources": res["sources"]
    })

print(json.dumps(results, ensure_ascii=False, indent=2))