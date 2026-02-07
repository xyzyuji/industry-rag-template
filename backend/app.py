from fastapi import FastAPI
import os

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/answer")
def answer(query: str):
    # いまのRAGロジックをここに繋ぐ
    return {"query": query, "answer": "dummy answer"}
