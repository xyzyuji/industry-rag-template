"""
Hackathon Public Edition: ローカル評価デモUI

- FastAPI を使わず、純粋にローカル関数を呼ぶ
- API版（public_api.py）とは別系統のデモ
"""

import streamlit as st
from answer_interface import answer
from simple_retrieve_fn import simple_retrieve_fn

st.title("RAG評価デモUI（Public版）")
question = st.text_input("質問を入力してください：")
k = st.slider("取得ドキュメント数", 1, 10, 5)

if st.button("評価実行"):
    result = answer(question, simple_retrieve_fn, k)
    st.write("## 回答")
    st.write(result["answer"])
    st.write("## 参照ドキュメント")
    st.write(result["docs"])
    st.write("## メトリクス")
    st.write(result["metrics"])
