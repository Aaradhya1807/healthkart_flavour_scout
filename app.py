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
st.subheader("AI-Powered Flavor Discovery")

ACCEPT_THRESHOLD = 75
MAX_FLAVOURS = 8

INTENT_STRICTNESS = 0.75
INTENT_THRESHOLD = int((1 - INTENT_STRICTNESS) * 100)

# ================== DECISION PIPELINE ==================
with st.expander("🔍 Click to understand the decision pipeline"):
    st.markdown("""
**Flavor Scout follows an explainable decision pipeline:**

### 📊 Data Collection
- Social media comments are collected as raw, unstructured input.

### 🧹 Signal Extraction
- Noise and irrelevant chatter are filtered out to capture real flavour intent.

### 📈 Trend & Sentiment Analysis
- Mentions are evaluated on:
  - Frequency  
  - Excitement  
  - Context  

### 🤖 LLM-based Scoring Engine
Each flavour is scored on:
- **Trend Strength**
- **Sentiment Strength**
- **Brand Fit**
- **Signal Quality**

### ✅ Decision Rules
- **Final Score ≥ 75 → ACCEPT**
- **Final Score < 75 → REJECT**
- **One Golden Candidate is recommended**
""")


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

# ================== LOAD DATA ==================
if data_source == "Live Reddit Comments (Beta)":
    keyword = st.text_input("Enter keyword / topic", value="whey protein")

    with st.spinner("Fetching Reddit comments..."):
        df = fetch_reddit_comments(keyword=keyword, limit=120)

    if df.empty:
        df = pd.read_csv("data/social_chatter.csv")

elif data_source == "Live YouTube Comments":
    query = st.text_input("Enter YouTube search query", value="protein flavours")

    with st.spinner("Fetching YouTube comments..."):
        comments = fetch_comments_by_query(query=query, max_videos=2, max_comments_per_video=25)

    if not comments:
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

    # ---------- DOMAIN GATE ----------
    FLAVOUR_CONTEXT_KEYWORDS = [
        "flavour", "flavor", "taste", "tasty", "sweet", "sour",
        "vanilla", "chocolate", "strawberry", "mango", "mint",
        "cookie", "banana", "whey", "protein", "shake",
        "ice cream", "drink"
    ]

    if not any(word in comments_text.lower() for word in FLAVOUR_CONTEXT_KEYWORDS):
        st.warning("⚠️ No flavours detected in comments.")
        st.stop()

    # ---------- PROMPT ----------
    prompt = f"""
You are a flavour extraction engine.

RULES:
- Output ONLY valid JSON
- No explanations, no markdown, no code
- Do NOT invent flavours
- Return at most {MAX_FLAVOURS} flavours

A flavour must be a concrete, edible or consumable taste.
Examples: vanilla, chocolate, mango mint, cookie blast.

INVALID:
- Brands
- Companies
- Tech terms
- Abstract concepts

If no flavours exist, return:
{{"decision_trace": []}}

FORMAT:
{{
  "decision_trace": [
    {{
      "flavor": "vanilla",
      "trend_score": 80,
      "signal_quality_score": 78,
      "final_score": 79
    }}
  ]
}}

COMMENTS:
{comments_text}
"""

    # ---------- AI CALL ----------
    response = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "Return ONLY valid JSON."},
            {"role": "user", "content": prompt}
        ],
        temperature=0,
        max_tokens=1200
    )

    raw_output = response.choices[0].message.content.strip()

    # ---------- SAFE JSON PARSE ----------
    def safe_json_load(text):
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1:
            return None
        try:
            return json.loads(text[start:end + 1])
        except json.JSONDecodeError:
            return None

    ai_output = safe_json_load(raw_output)

    if not ai_output:
        st.error("❌ AI returned invalid JSON")
        st.code(raw_output)
        st.stop()

    decision_trace = ai_output.get("decision_trace", [])
    if not decision_trace:
        st.warning("⚠️ No flavours detected in comments.")
        st.stop()

    trace_df = pd.DataFrame(decision_trace)

    # ---------- HARD FILTER ----------
    BRAND_KEYWORDS = [
        "ryse", "ghost", "optimum", "dymatize",
        "labrada", "ascent", "myprotein",
        "samsung", "oppo", "redmi", "iphone"
    ]

    def is_valid_flavour(flavour):
        flavour = flavour.lower()
        if len(flavour.split()) > 3:
            return False
        if any(b in flavour for b in BRAND_KEYWORDS):
            return False
        return True

    trace_df = trace_df[trace_df["flavor"].apply(is_valid_flavour)]

    if trace_df.empty:
        st.warning("⚠️ No flavours detected in comments.")
        st.stop()

    trace_df = trace_df.head(MAX_FLAVOURS)

    # ---------- RANK CALIBRATION ----------
    trace_df = trace_df.sort_values(
        by=["trend_score", "signal_quality_score"],
        ascending=False
    ).reset_index(drop=True)

    n = len(trace_df)
    MAX_SCORE, MIN_SCORE = 100, 40
    step = (MAX_SCORE - MIN_SCORE) / (n - 1) if n > 1 else 0

    trace_df["final_score"] = [int(MAX_SCORE - i * step) for i in range(n)]
    trace_df["trend_score"] = trace_df["final_score"]
    trace_df["signal_quality_score"] = trace_df["final_score"]

    trace_df["decision"] = trace_df["final_score"].apply(
        lambda x: "ACCEPT" if x >= ACCEPT_THRESHOLD else "REJECT"
    )

    # ---------- SCORE-AWARE REASON ----------
    def intent_reason(row):
        score = row["final_score"]
        flavour = row["flavor"]

        if score >= 95:
            return f"Overwhelmingly positive sentiment for {flavour}."
        elif score >= 85:
            return f"Strong positive perception for {flavour} with minor neutral feedback."
        elif score >= 75:
            return f"Generally liked flavour with some mixed opinions."
        elif score >= 60:
            return f"Mixed sentiment with noticeable criticism."
        elif score >= 40:
            return f"Predominantly negative feedback affecting appeal."
        else:
            return f"Strong negative sentiment across user comments."

    trace_df["reason"] = trace_df.apply(intent_reason, axis=1)

    # ================== TREND WALL (BAR GRAPH) ==================
    st.markdown("## 🔥 Trend Wall (Flavor Popularity)")

    # Prepare data
    trend_df = trace_df[["flavor", "final_score"]].set_index("flavor")

    # Bar chart
    st.bar_chart(trend_df)



    # ---------- DISPLAY ----------
    st.markdown("## 📋 Decision Trace")
    st.dataframe(trace_df, use_container_width=True)

    st.markdown("## 🏆 Golden Candidate")
    accepted = trace_df[trace_df["decision"] == "ACCEPT"]

    if accepted.empty:
        st.error("❌ No flavour met acceptance criteria.")
    else:
        top = accepted.iloc[0]
        st.success(f"🚀 {top['flavor']} (Score: {top['final_score']})")
