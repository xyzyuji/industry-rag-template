"""
Hackathon Public Edition: 評価ロジックのコア

- 失敗の類型化（failure_tags）を重視
- 点数づけではなく、運用判断の起点を提供
- 本番ロジックは非公開（private版で管理）
"""

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
            "sources": ["source_doc.txt"],
        }
    if "Cloud" in query:
        return {
            "generated": "Cloud RunでRAGを運用できます。",
            "sources": [],  # あえて出典なし（hallucination デモ）
        }
    return {
        "generated": "これはサンプル回答です。",
        "sources": [],
    }


# ==============================
# ====== 評価ロジック（簡易）=====
# ==============================

def check_must_include(generated: str, must_include: list) -> dict:
    """must_include の各語が含まれているかを詳細に判定"""
    detail = {kw: (kw in generated) for kw in must_include}
    return {"all_ok": all(detail.values()), "detail": detail}


def check_hallucination(generated: str, sources: list) -> bool:
    """出典と回答内容から簡易的に hallucination を判定"""
    # 出典が空なら要注意
    if len(sources) == 0:
        return True

    # 回答が極端に短い場合も要注意
    if len(generated) < 10:
        return True

    return False


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
        "ideal_answer": "keyword1とkeyword2を含む回答",
    },
    {
        "qid": "q2",
        "type": "rag",
        "must_include": ["Cloud", "運用"],
        "ideal_answer": "CloudでRAGを運用できる説明",
    },
    {
        "qid": "q3",
        "type": "rag",
        "must_include": ["example"],
        "ideal_answer": "exampleを含む説明",
    },
]


# ==============================
# ====== コア評価 ======
# ==============================

def evaluate_one(question: str, must_include: list, ideal_answer: str):
    res = answer(question)

    must_include_result = check_must_include(res["generated"], must_include)
    hallucination = check_hallucination(res["generated"], res["sources"])
    similarity = dummy_similarity(res["generated"], ideal_answer)

    failure_tags = []
    if not must_include_result["all_ok"]:
        failure_tags.append("missing_must_include")
    if hallucination:
        failure_tags.append("hallucination")

    suggested_action = "要調査" if failure_tags else "OK"

    return {
        "must_include": must_include_result,
        "hallucination": hallucination,
        "similarity": similarity,
        "failure_tags": failure_tags,
        "suggested_action": suggested_action,
        "generated": res["generated"],
        "sources": res["sources"],
    }
