from fastapi import FastAPI
from public.answer_interface import answer
from public.simple_retrieve_fn import simple_retrieve_fn
from public.evaluate_public import check_must_include, check_hallucination

app = FastAPI()

@app.post("/answer")
def answer_api(payload: dict):
    q = payload.get("question")
    k = payload.get("k", 5)
    res = answer(q, simple_retrieve_fn, k)
    return res

@app.post("/evaluate")
def evaluate_api(payload: dict):
    q = payload["question"]
    must_include = payload["must_include"]
    res = answer(q, simple_retrieve_fn, 5)
    return {
        "generated": res["answer"],
        "must_include_ok": check_must_include(res["answer"], must_include),
        # Public版として「docsが空ならhallucination扱い」という簡易ルールに統一
        "hallucination": len(res["docs"]) == 0,
    }
