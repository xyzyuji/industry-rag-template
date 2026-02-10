"""Gemini API クライアント（Hackathon Public Edition 用の最小ラッパー）"""

import os
from typing import Optional

from google import genai


# AI Studio のサンプルと同等のモデル指定（必要に応じて変更）
_GEMINI_MODEL = "gemini-3-flash-preview"


def _get_api_key() -> Optional[str]:
    return os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")


def generate_answer(question: str) -> str:
    """Gemini に質問を投げて回答テキストを返すシンプルなラッパー。

    環境変数 GEMINI_API_KEY / GOOGLE_API_KEY のいずれかが必要。
    """

    api_key = _get_api_key()
    if not api_key:
        # API キー未設定時でもAPI自体は落とさず、メッセージで伝える
        return "[Gemini APIキーが設定されていません。GEMINI_API_KEY を Cloud Run の環境変数に設定してください。]"

    # 公式サンプルと同じ Client ベースの呼び出し
    client = genai.Client(api_key=api_key)

    try:
        response = client.models.generate_content(
            model=_GEMINI_MODEL,
            contents=question,
        )
    except Exception as e:  # 外部API例外は握りつぶしてメッセージ化
        return f"[Gemini呼び出し中にエラーが発生しました: {e}]"

    # text プロパティがない／空のケースもケア
    return (getattr(response, "text", None) or "[Geminiから有効なテキストが返りませんでした]")
