import streamlit as st
import pandas as pd
import os
import json
from dotenv import load_dotenv
from groq import Groq

from reddit_ingest import fetch_reddit_comments
from youtube_ingest import fetch_comments_by_query


# ================== SETUP ==================
load_dotenv()

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

st.set_page_config(page_title="Flavor Scout Engine", layout="wide")

st.title("🍽️ Flavor Scout Engine")
st.subheader("AI-Powered Flavor Discovery for HealthKart")

ACCEPT_THRESHOLD = 75


# ================== DATA SOURCE ==================
st.markdown("## 📥 Data Source")

data_source = st.selectbox(
    "Select input source",
    [
        "Sample Dataset",
        "Live Reddit Comments (Beta)",
        "Live YouTube Comments"
    ]
)


# ================== DECISION PIPELINE ==================
st.markdown("## 🧠 Decision Pipeline (Explainability)")

with st.expander("Click to understand how flavour decisions are made"):
    st.markdown("""
### 1️⃣ Data Collection
Consumer conversations are collected from **public platforms**
such as **Reddit and YouTube**.

---

### 2️⃣ Signal Extraction
Only **flavour-related signals** are retained:
- Explicit flavour mentions (*chocolate, vanilla*)
- Implicit mentions (*tastes like vanilla*)
- Preference or dislike

---

### 3️⃣ Semantic Understanding
Each signal is evaluated for:
- Flavour name
- Intent clarity
- Strength of mention

---

### 4️⃣ AI Scoring (Advisory Only)
AI assigns:
- **Trend Score (0–100)** → frequency & buzz
- **Signal Quality Score (0–100)** → clarity of intent
- **Final Score (0–100)** → conservative estimate

⚠️ AI does NOT decide acceptance.

---

### 5️⃣ Hard Business Rule
Application enforces:
- Final Score ≥ **75** → ACCEPT
- Final Score < **75** → REJECT

---

### 6️⃣ Golden Candidate
Highest scoring **ACCEPTED flavour**
is recommended for validation.
""")


# ================== LOAD DATA ==================
if data_source == "Live Reddit Comments (Beta)":
    keyword = st.text_input("Enter keyword / flavor to analyze", value="whey protein")

    with st.spinner("Fetching Reddit comments..."):
        df = fetch_reddit_comments(keyword=keyword, limit=120)

    if df.empty:
        st.warning("⚠️ Reddit limit hit. Loading sample data.")
        df = pd.read_csv("data/social_chatter.csv")

elif data_source == "Live YouTube Comments":
    query = st.text_input("Enter YouTube search query", value="protein flavours")

    with st.spinner("Fetching YouTube comments..."):
        comments = fetch_comments_by_query(
            query=query,
            max_videos=5,
            max_comments_per_video=10
        )

    if not comments:
        st.warning("⚠️ Unable to fetch YouTube comments. Loading sample data.")
        df = pd.read_csv("data/social_chatter.csv")
    else:
        df = pd.DataFrame(comments).rename(columns={"text": "comment"})

else:
    df = pd.read_csv("data/social_chatter.csv")


# ================== DISPLAY DATA ==================
st.markdown("### 💬 Social Media Chatter")
st.write(f"Loaded **{len(df)}** comments")
st.dataframe(df, use_container_width=True)


# ================== AI ANALYSIS ==================
st.markdown("## 🤖 AI Decision Engine")

if st.button("🔍 Analyze with AI"):

    comments_text = "\n".join(df["comment"].astype(str).tolist())

    prompt = f"""
You are a flavour signal extraction engine.

STRICT RULES:
- Final_score should be the average of Signal_quality_score and trend_score
- Output ONLY valid JSON
- NO python code
- NO calculations
- NO variables
- NO explanations
- Use conservative scoring, every score must be an integer from 1 to 100.
- Scores MUST vary between flavours
- Not all flavours can have same score
- If no flavour intent exists, return empty decision_trace []
- If the query for youtube is something in which you think comments will not have flavours, like if the query is "Mobiles", it is obv that comments will not have flavours, you can show the output as, "No flavours found in comments".

Allowed flavours:
- Food and dessert flavours
- Do NOT invent flavours
- Do not take random words with intended flavours like if a comment is "This one is the worst", dont take this, even if this shows intent, it has no flavour.

FORMAT (EXACT):

{{
  "decision_trace": [
    {{
      "flavor": "",
      "trend_score": 0,
      "signal_quality_score": 0,
      "final_score": 0
    }}
  ]
}}

COMMENTS:
{comments_text}
"""

    with st.spinner("AI is analyzing social chatter..."):
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": "You output ONLY valid JSON. No text. No code."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            max_tokens=3000
        )

        raw_output = response.choices[0].message.content.strip()

    # ================== HARD JSON GUARD ==================
    if not raw_output.startswith("{"):
        st.error("❌ AI did not return JSON")
        st.code(raw_output)
        st.stop()

    try:
        ai_output = json.loads(raw_output)
    except json.JSONDecodeError:
        st.error("⚠️ AI output could not be parsed")
        st.code(raw_output)
        st.stop()


    # ================== DECISION TRACE ==================
    trace_df = pd.DataFrame(ai_output.get("decision_trace", []))

    if trace_df.empty:
        st.warning("⚠️ No flavour intent detected.")
        st.stop()


    # ================== HARD BUSINESS RULE ==================
    trace_df["decision"] = trace_df["final_score"].apply(
        lambda x: "ACCEPT" if x >= ACCEPT_THRESHOLD else "REJECT"
    )

    trace_df["reason"] = trace_df["decision"].apply(
        lambda x: "Meets acceptance threshold" if x == "ACCEPT" else "Below acceptance threshold"
    )


    # ================== DISPLAY TRACE ==================
    st.markdown("## 📋 Decision Trace")
    st.dataframe(trace_df, use_container_width=True)


    # ================== TREND WALL ==================
    st.markdown("## 📊 Trend Wall")
    st.bar_chart(trace_df.set_index("flavor")["trend_score"])


    # ================== GOLDEN CANDIDATE ==================
    st.markdown("## 🏆 Golden Candidate Recommendation")

    accepted_df = trace_df[trace_df["decision"] == "ACCEPT"]

    if accepted_df.empty:
        st.error("❌ No flavour met acceptance threshold.")
    else:
        golden = accepted_df.sort_values("final_score", ascending=False).iloc[0]

        st.markdown(
            f"""
<div style="padding:30px;border-radius:15px;background:#0f172a;color:white">
<h2>🚀 {golden['flavor']}</h2>
<p><strong>Final Score:</strong> {golden['final_score']}</p>
<p>Highest scoring accepted flavour</p>
</div>
""",
            unsafe_allow_html=True
        )
