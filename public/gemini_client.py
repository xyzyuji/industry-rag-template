"""Gemini API クライアント（Hackathon Public Edition 用の最小ラッパー）"""

import os
from typing import Optional

import google.generativeai as genai


# v1beta API で安定して利用可能なテキストモデルを指定
_GEMINI_MODEL = "gemini-1.0-pro"


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

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(_GEMINI_MODEL)

    try:
        response = model.generate_content(question)
    except Exception as e:  # 外部API例外は握りつぶしてメッセージ化
        return f"[Gemini呼び出し中にエラーが発生しました: {e}]"

    # text プロパティがない／空のケースもケア
    return (getattr(response, "text", None) or "[Geminiから有効なテキストが返りませんでした]")
