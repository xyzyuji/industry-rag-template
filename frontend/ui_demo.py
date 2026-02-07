import streamlit as st
import requests

# ★ここは実際のCloud Run APIのURLに置き換えてください
API_URL = "https://industry-rag-api-xxxxxxxx.a.run.app"

st.title("Industry RAG Demo")

query = st.text_input("質問を入力してください")

if st.button("送信"):
    res = requests.post(
        f"{API_URL}/answer",
        params={"query": query}
    )
    st.write(res.json())
