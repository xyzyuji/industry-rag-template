"""
Hackathon Public Edition: 互換CLIエントリ

- 旧 evaluate_public.py を残し、evaluate_cli に委譲
- 評価ロジックの一部関数もここから再エクスポート
"""

from public.evaluate_cli import run
from public.evaluate_core import check_must_include, check_hallucination

__all__ = ["run", "check_must_include", "check_hallucination"]


if __name__ == "__main__":
    run()