"""
Hackathon Public Edition: 評価デモ用 API

- RAGの「外形（API）」のみ公開
- 内部ロジックは public/answer_interface.py に委譲
- 本番ロジックは非公開（本リポジトリ外）
"""

from fastapi import FastAPI
from pydantic import BaseModel
from public.answer_interface import answer
from public.simple_retrieve_fn import simple_retrieve_fn
from public.evaluate_public import check_must_include, check_hallucination


app = FastAPI(
    title="RAG Evaluation Template (Public API)",
    description="Hackathon Public Edition のデモ API (DEPLOY 2026-02-09)",
)


class AnswerRequest(BaseModel):
    question: str
    k: int = 5


class EvaluateRequest(BaseModel):
    question: str
    must_include: list[str]


@app.get("/")
def root():
    return {
        "name": "rag-public-api",
        "message": "RAG Evaluation Template (Public Edition)",
        "endpoints": ["/answer", "/evaluate", "/health"],
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/answer")
def answer_api(req: AnswerRequest):
    res = answer(req.question, simple_retrieve_fn, req.k)
    return res


@app.post("/evaluate")
def evaluate_api(req: EvaluateRequest):
    res = answer(req.question, simple_retrieve_fn, 5)
    must_include_result = check_must_include(res["answer"], req.must_include)
    hallucination = check_hallucination(res["answer"], res["docs"])
    return {
        "generated": res["answer"],
        "must_include": must_include_result,
        "hallucination": hallucination,
    }
