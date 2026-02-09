import streamlit as st
import requests

# ★ここは実際のCloud Run APIのURLに置き換え
API_URL = "https://industry-rag-template-api-873508214410.asia-northeast1.run.app"

st.title("Industry RAG Demo")

# --- サンプル入力プリセット（Evaluation Scenarios） ---
if "question_input" not in st.session_state:
    st.session_state["question_input"] = ""
if "must_include_input" not in st.session_state:
    st.session_state["must_include_input"] = ""

sample_cases = {
    "（サンプルなし）": {"question": "", "must_include": ""},
    "Case 1: 正しい回答（理想ケース）": {
        "question": "このテンプレートの目的と特徴を教えてください。",
        "must_include": "RAG, 評価, Cloud Run",
    },
    "Case 2: 明確に間違った回答（NGケース）": {
        "question": "このリポジトリは画像生成モデルですか？",
        "must_include": "テキスト検索, RAG",
    },
    "Case 3: 検索はダメだが回答は正しい": {
        "question": "RAGとは何か、一般的な概念を説明してください。",
        "must_include": "検索, 外部知識",
    },
    "Case 4: 一部だけ満たしている（部分OK）": {
        "question": "Cloud Run上でRAG APIを動かすときのポイントは？",
        "must_include": "Cloud Run, 評価, GitHub連携",
    },
    "Case 5: 長くてそれっぽいが怪しい": {
        "question": "このテンプレートを使うと、どんなRAGシステムでも完全自動で運用できますか？",
        "must_include": "制約, 改善サイクル",
    },
}

selected_sample = st.selectbox(
    "サンプル入力（Evaluation Scenario）",
    list(sample_cases.keys()),
    index=0,
    help="READMEに記載しているEvaluation Scenariosに対応したサンプル入力です。選ぶと質問とmust_includeが自動入力されます。",
)

if selected_sample != "（サンプルなし）":
    st.session_state["question_input"] = sample_cases[selected_sample]["question"]
    st.session_state["must_include_input"] = sample_cases[selected_sample]["must_include"]

question = st.text_input("質問を入力してください", key="question_input")
k = st.slider("取得ドキュメント数", 1, 10, 5)
must_include_text = st.text_input("must_include（カンマ区切り）", key="must_include_input")

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
    data = res.json()

    st.write("### 評価結果 (raw)")
    st.json(data)

    # Case分類用の簡易ロジック（READMEのEvaluation Scenariosに対応）
    case_label = None
    desc = None

    generated = data.get("generated", "")
    must = data.get("must_include", {})
    all_ok = must.get("all_ok")
    detail = must.get("detail", {})
    hallucination = data.get("hallucination")

    # Case 1: 正しい回答（理想ケース）
    if all_ok and hallucination is False:
        case_label = "Case 1: 正しい回答（理想ケース）"
        desc = "RAGが正しく機能すると、必須キーワードを全て満たし、hallucination も False になります。"

    # Case 2: 明確に間違った回答（NGケース）
    elif all_ok is False and hallucination is True and all(v is False for v in detail.values()):
        case_label = "Case 2: 明確に間違った回答（NGケース）"
        desc = "must_include を全く満たしておらず、hallucination も True となる“ダメな回答”の例です。"

    # Case 3: 検索はダメだが回答は正しい（人間判断が必要なケース）
    elif hallucination is True and generated and all(v is False for v in detail.values()):
        case_label = "Case 3: 検索はダメだが回答は正しい（人間判断が必要なケース）"
        desc = "docs が取得できず hallucination=True だが、回答自体は一般的に正しい可能性があるケースです。"

    # Case 4: 一部だけ満たしているケース（部分OK）
    elif all_ok is False and detail and any(detail.values()):
        case_label = "Case 4: 一部だけ満たしているケース（部分OK）"
        desc = "必須キーワードの一部のみを満たしており、どこが不足しているかを detail から確認できます。"

    # Case 5: 長くてそれっぽいが怪しい回答（微妙ケース）
    elif all_ok and hallucination is True:
        case_label = "Case 5: 長くてそれっぽいが怪しい回答（微妙ケース）"
        desc = "キーワード的には条件を満たしていても、出典状況などから hallucination=True となる例です。"

    if case_label:
        st.write("### 解釈（Evaluation Scenario）")
        st.markdown(f"**{case_label}**")
        st.write(desc)
    else:
        st.write("### 解釈")
        st.write("どのCaseにも明確には当てはまりませんが、`must_include` と `hallucination` の組み合わせから状態を読み取れます。")
