import streamlit as st
import requests

# ★ここは実際のCloud Run APIのURLに置き換え
API_URL = "https://industry-rag-template-api-873508214410.asia-northeast1.run.app"

st.title("Industry RAG Demo")

question = st.text_input("質問を入力してください")
k = st.slider("取得ドキュメント数", 1, 10, 5)
must_include_text = st.text_input("must_include（カンマ区切り）")

if st.button("送信"):
    res = requests.post(
        f"{API_URL}/answer",
        json={"question": question, "k": k},
        timeout=30,
    )
    st.write(res.json())

if st.button("評価"):
    must_include = [s.strip() for s in must_include_text.split(",") if s.strip()]
    res = requests.post(
        f"{API_URL}/evaluate",
        json={"question": question, "must_include": must_include},
        timeout=30,
    )
    st.write(res.json())
