import streamlit as st
import pandas as pd
import os
import json
from dotenv import load_dotenv
from openai import OpenAI

from reddit_ingest import fetch_reddit_comments
from youtube_ingest import fetch_comments_by_query


# ------------------ SETUP ------------------
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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
**Flavor Scout follows an explainable decision pipeline:**

1️⃣ **Data Collection**  
Live and cached social media comments are ingested.

2️⃣ **Signal Extraction**  
Noise is reduced to isolate meaningful flavor-related discussion.

3️⃣ **Semantic Trend & Sentiment Analysis**  
Implicit flavor intent is inferred from context.

4️⃣ **LLM-based Scoring Engine**  
Each flavor is scored on:
- Trend Strength  
- Sentiment Strength  
- Brand Fit  
- Signal Quality  

5️⃣ **Decision Rules**
- Final Score ≥ 75 → ACCEPT  
- Final Score < 75 → REJECT  
- One Golden Candidate is recommended
""")


# ------------------ LOAD DATA ------------------
if data_source == "Live Reddit Comments (Beta)":
    keyword = st.text_input(
        "Enter keyword / flavor to analyze",
        value="whey protein"
    )

    with st.spinner("Fetching Reddit comments..."):
        df = fetch_reddit_comments(keyword=keyword, limit=120)

    if df.empty:
        st.warning(
            "⚠️ Reddit API limitations detected. Showing representative sample data."
        )
        df = pd.read_csv("data/social_chatter.csv")

elif data_source == "Live YouTube Comments":
    query = st.text_input(
        "Enter YouTube search query",
        value="best whey protein india"
    )

    with st.spinner("Fetching YouTube comments..."):
        comments = fetch_comments_by_query(
            query=query,
            max_videos=10,
            max_comments_per_video=50
        )

    if not comments:
        st.warning(
            "⚠️ Unable to fetch live YouTube comments. Showing sample data instead."
        )
        df = pd.read_csv("data/social_chatter.csv")
    else:
        df = pd.DataFrame(comments)
        df = df.rename(columns={"text": "comment"})

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

SCORING (0–100):
- trend_score
- sentiment_score
- brand_fit_score
- signal_quality_score

FINAL_SCORE = average of all four scores

RULES:
- FINAL_SCORE >= 75 → ACCEPT
- FINAL_SCORE < 75 → REJECT
- Scores above 85 should be rare

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
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )

    raw_output = response.choices[0].message.content.strip()

    if raw_output.startswith("```"):
        raw_output = raw_output.replace("```json", "").replace("```", "").strip()

    if "{" in raw_output and "}" in raw_output:
        raw_output = raw_output[raw_output.find("{"): raw_output.rfind("}") + 1]

    try:
        ai_output = json.loads(raw_output)
    except json.JSONDecodeError:
        st.error("⚠️ AI output could not be parsed as JSON.")
        st.stop()


    # ------------------ DECISION TRACE ------------------
    st.markdown("## 📋 Decision Trace")

    trace_df = pd.DataFrame(ai_output["decision_trace"])

    st.dataframe(
        trace_df[
            [
                "flavor",
                "trend_score",
                "sentiment_score",
                "brand_fit_score",
                "signal_quality_score",
                "final_score",
                "decision"
            ]
        ],
        use_container_width=True
    )


    # ------------------ TREND WALL (AI-ALIGNED) ------------------
    st.markdown("## 📊 Trend Wall (AI-Evaluated)")

    trend_wall_df = trace_df[["flavor", "trend_score"]].set_index("flavor")
    st.bar_chart(trend_wall_df)


    # ------------------ DECISION BREAKDOWN ------------------
    st.markdown("## 🧠 Decision Breakdown")

    for item in ai_output["decision_trace"]:
        if item["decision"] == "ACCEPT":
            st.success(
                f"""
**{item['flavor']}** — {item['brand']}  
**Final Score:** {item['final_score']}  

{item['reason']}
"""
            )
        else:
            st.error(
                f"""
**{item['flavor']}**  
**Final Score:** {item['final_score']}  

Rejected because: {item['reason']}
"""
            )


    # ------------------ GOLDEN CANDIDATE ------------------
    gc = ai_output["golden_candidate"]

    st.markdown("## 🏆 Golden Candidate Recommendation")

    st.markdown(
        f"""
<div style="
    padding: 30px;
    border-radius: 15px;
    background-color: #0f172a;
    color: white;
">
    <h2>🚀 {gc['flavor']} — {gc['brand']}</h2>
    <p><strong>Final Score:</strong> {gc['final_score']}</p>
    <p style="font-size:18px;">{gc['why']}</p>
</div>
""",
        unsafe_allow_html=True
    )
