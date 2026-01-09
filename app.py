import streamlit as st
import pandas as pd
import os
import json
from dotenv import load_dotenv
from openai import OpenAI, RateLimitError, OpenAIError
import google.generativeai as genai

from reddit_ingest import fetch_reddit_comments
from youtube_ingest import fetch_comments_by_query


# ------------------ SETUP ------------------
load_dotenv()

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
gemini_model = genai.GenerativeModel("gemini-1.5-flash")

st.set_page_config(page_title="Flavor Scout Engine", layout="wide")

st.title("🍽️ Flavor Scout Engine")
st.subheader("AI-Powered Flavor Discovery for HealthKart")


# ------------------ DATA SOURCE ------------------
st.markdown("## 📥 Data Source")

data_source = st.selectbox(
    "Select input source",
    [
        "Sample Dataset",
        "Live Reddit Comments (Beta)",
        "Live YouTube Comments"
    ]
)


# ------------------ EXPLAINABILITY ------------------
st.markdown("## 🧠 How Flavor Decisions Are Made")

with st.expander("Click to understand the decision pipeline"):
    st.markdown("""
1️⃣ Data Collection  
2️⃣ Signal Extraction  
3️⃣ Semantic Trend & Sentiment Analysis  
4️⃣ LLM-based Scoring Engine  
5️⃣ Decision Rules
""")


# ------------------ LOAD DATA ------------------
if data_source == "Live Reddit Comments (Beta)":
    keyword = st.text_input("Enter keyword / flavor to analyze", value="whey protein")

    with st.spinner("Fetching Reddit comments..."):
        df = fetch_reddit_comments(keyword=keyword, limit=120)

    if df.empty:
        st.warning("⚠️ Reddit API limit hit. Showing sample data.")
        df = pd.read_csv("data/social_chatter.csv")

elif data_source == "Live YouTube Comments":
    query = st.text_input("Enter YouTube search query", value="protein flavours")

    with st.spinner("Fetching YouTube comments..."):
        comments = fetch_comments_by_query(
            query=query,
            max_videos=10,
            max_comments_per_video=10
        )

    if not comments:
        st.warning("⚠️ Unable to fetch YouTube comments. Showing sample data.")
        df = pd.read_csv("data/social_chatter.csv")
    else:
        df = pd.DataFrame(comments).rename(columns={"text": "comment"})

else:
    df = pd.read_csv("data/social_chatter.csv")


# ------------------ DISPLAY DATA ------------------
st.markdown("### 💬 Social Media Chatter")
st.write(f"Loaded **{len(df)}** comments")
st.dataframe(df, use_container_width=True)


# ------------------ AI ANALYSIS ------------------
st.markdown("## 🤖 AI Decision Engine")

if st.button("🔍 Analyze with AI"):

    comments_text = "\n".join(df["comment"].astype(str).tolist())

    prompt = f"""
You are a product analyst at HealthKart.

Evaluate flavor ideas using a structured scoring framework.

Return STRICT JSON only.

FORMAT:
{{
  "decision_trace": [
    {{
      "flavor": "",
      "brand": "",
      "trend_score": 0,
      "sentiment_score": 0,
      "brand_fit_score": 0,
      "signal_quality_score": 0,
      "final_score": 0,
      "decision": "ACCEPT / REJECT",
      "reason": ""
    }}
  ],
  "golden_candidate": {{
    "flavor": "",
    "brand": "",
    "final_score": 0,
    "why": ""
  }}
}}

COMMENTS:
{comments_text}
"""

    with st.spinner("AI is analyzing social chatter..."):

        try:
            # ---------- PRIMARY: GPT-4o ----------
            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=800
            )

            raw_output = response.choices[0].message.content

        except (RateLimitError, OpenAIError):
            # ---------- FALLBACK: GEMINI ----------
            st.warning("⚠️ Transferring AI from GPT-4o to Gemini")

            gemini_response = gemini_model.generate_content(prompt)
            raw_output = gemini_response.text


    # ------------------ CLEAN & PARSE JSON ------------------
    raw_output = raw_output.strip()

    if raw_output.startswith("```"):
        raw_output = raw_output.replace("```json", "").replace("```", "").strip()

    raw_output = raw_output[raw_output.find("{"): raw_output.rfind("}") + 1]

    try:
        ai_output = json.loads(raw_output)
    except json.JSONDecodeError:
        st.error("⚠️ AI output could not be parsed as JSON.")
        st.stop()


    # ------------------ DECISION TRACE ------------------
    st.markdown("## 📋 Decision Trace")

    trace_df = pd.DataFrame(ai_output["decision_trace"])
    st.dataframe(trace_df, use_container_width=True)


    # ------------------ TREND WALL ------------------
    st.markdown("## 📊 Trend Wall")

    if not trace_df.empty:
        st.bar_chart(trace_df.set_index("flavor")["trend_score"])


    # ------------------ GOLDEN CANDIDATE ------------------
    gc = ai_output["golden_candidate"]

    st.markdown("## 🏆 Golden Candidate Recommendation")

    st.markdown(
        f"""
<div style="padding:30px;border-radius:15px;background:#0f172a;color:white">
<h2>🚀 {gc['flavor']} — {gc['brand']}</h2>
<p><strong>Final Score:</strong> {gc['final_score']}</p>
<p>{gc['why']}</p>
</div>
""",
        unsafe_allow_html=True
    )
