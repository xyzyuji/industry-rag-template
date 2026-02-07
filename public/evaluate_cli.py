"""
Hackathon Public Edition: CLI 実行用ラッパー

- evaluate_core の結果をまとめて出力
"""

import json
from public.evaluate_core import evaluate_one, questions


def run():
    results = []
    for q in questions:
        result = evaluate_one(q["qid"], q["must_include"], q["ideal_answer"])
        result["qid"] = q["qid"]
        results.append(result)

    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    run()
