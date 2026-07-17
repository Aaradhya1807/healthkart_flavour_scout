import streamlit as st
import pandas as pd
import os
import json
from dotenv import load_dotenv
from groq import Groq

from reddit_ingest import fetch_reddit_comments, get_disabled_reason
from youtube_ingest import fetch_comments_by_query

# ================== SETUP ==================
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

st.set_page_config(page_title="Flavor Scout Engine", layout="wide")

st.title("🍽️ Flavor Scout Engine")
st.subheader("AI-Powered Flavor Discovery")

ACCEPT_THRESHOLD = 75
MAX_FLAVOURS = 8

# Weights for the composite score. These are the same four components
# advertised in the pipeline explainer below, so the number shown to the
# user is actually derived from them (not a rank-based placeholder).
SCORE_WEIGHTS = {
    "trend_score": 0.35,
    "sentiment_score": 0.30,
    "brand_fit_score": 0.20,
    "signal_quality_score": 0.15,
}

FLAVOUR_CONTEXT_KEYWORDS = [
    "flavour", "flavor", "taste", "tasty", "sweet", "sour",
    "vanilla", "chocolate", "strawberry", "mango", "mint",
    "cookie", "banana", "whey", "protein", "shake",
    "ice cream", "drink",
]

BRAND_KEYWORDS = [
    "ryse", "ghost", "optimum", "dymatize",
    "labrada", "ascent", "myprotein",
    "samsung", "oppo", "redmi", "iphone",
]

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
- **Trend Strength** (35% weight)
- **Sentiment Strength** (30% weight)
- **Brand Fit** (20% weight)
- **Signal Quality** (15% weight)

The final score is a weighted average of these four components — not a
ranking placeholder — so the same flavour will score the same regardless
of what else appears in the batch.

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
        "Live Reddit Comments (Disabled — policy)",
        "Live YouTube Comments",
    ],
)


@st.cache_data(ttl=600, show_spinner=False)
def load_reddit(keyword: str, limit: int) -> pd.DataFrame:
    return fetch_reddit_comments(keyword=keyword, limit=limit)


@st.cache_data(ttl=600, show_spinner=False)
def load_youtube(query: str, max_videos: int, max_comments_per_video: int) -> list:
    return fetch_comments_by_query(
        query=query,
        max_videos=max_videos,
        max_comments_per_video=max_comments_per_video,
    )


# ================== LOAD DATA ==================
if data_source == "Live Reddit Comments (Disabled — policy)":
    keyword = st.text_input("Enter keyword / topic", value="whey protein")

    with st.spinner("Fetching Reddit comments..."):
        df = load_reddit(keyword, 120)

    if df.empty:
        st.info(f"{get_disabled_reason()} Showing sample data instead.")
        df = pd.read_csv("data/social_chatter.csv")

elif data_source == "Live YouTube Comments":
    query = st.text_input("Enter YouTube search query", value="protein flavours")

    with st.spinner("Fetching YouTube comments..."):
        comments = load_youtube(query, 2, 25)

    if not comments:
        st.info("Live YouTube fetch returned nothing (missing API key, quota exceeded, "
                "or no matching videos) — showing sample data instead.")
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

    if groq_client is None:
        st.error("❌ GROQ_API_KEY is not set. Add it to your .env file to run analysis.")
        st.stop()

    comments_text = "\n".join(df["comment"].astype(str).tolist())

    # ---------- DOMAIN GATE ----------
    if not any(word in comments_text.lower() for word in FLAVOUR_CONTEXT_KEYWORDS):
        st.warning("⚠️ No flavours detected in comments.")
        st.stop()

    # ---------- PROMPT ----------
    prompt = f"""
You are a flavour extraction and scoring engine.

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

Score each flavour from 0-100 on FOUR independent components based only
on evidence in the comments:
- trend_score: how frequently and prominently it's mentioned
- sentiment_score: how positively people react to it
- brand_fit_score: how well it fits a nutrition/protein/supplement brand
- signal_quality_score: how clear and unambiguous the mentions are (vs vague/sarcastic)

Do NOT compute a final score yourself — just return the four component
scores per flavour, honestly and independently of each other.

If no flavours exist, return:
{{"decision_trace": []}}

FORMAT:
{{
  "decision_trace": [
    {{
      "flavor": "vanilla",
      "trend_score": 80,
      "sentiment_score": 85,
      "brand_fit_score": 70,
      "signal_quality_score": 78
    }}
  ]
}}

COMMENTS:
{comments_text}
"""

    # ---------- AI CALL ----------
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "Return ONLY valid JSON."},
                {"role": "user", "content": prompt},
            ],
            temperature=0,
            max_tokens=1200,
        )
        raw_output = response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"❌ AI request failed: {e}")
        st.stop()

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

    # Fill any missing component scores defensively (LLM output isn't
    # guaranteed to include every key for every row).
    for col in SCORE_WEIGHTS:
        if col not in trace_df.columns:
            trace_df[col] = 50
        trace_df[col] = pd.to_numeric(trace_df[col], errors="coerce").fillna(50).clip(0, 100)

    # ---------- HARD FILTER ----------
    def is_valid_flavour(flavour):
        flavour = str(flavour).lower()
        if len(flavour.split()) > 3:
            return False
        if any(b in flavour for b in BRAND_KEYWORDS):
            return False
        return True

    trace_df = trace_df[trace_df["flavor"].apply(is_valid_flavour)]

    if trace_df.empty:
        st.warning("⚠️ No flavours detected in comments.")
        st.stop()

    # ---------- REAL WEIGHTED SCORING ----------
    # final_score is a genuine weighted average of the four LLM-scored
    # components — each flavour's score depends only on itself, not on
    # its rank relative to the others in this batch.
    trace_df["final_score"] = sum(
        trace_df[col] * weight for col, weight in SCORE_WEIGHTS.items()
    ).round().astype(int)

    trace_df = trace_df.sort_values(by="final_score", ascending=False).reset_index(drop=True)
    trace_df = trace_df.head(MAX_FLAVOURS)

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
    trend_df = trace_df[["flavor", "final_score"]].set_index("flavor")
    st.bar_chart(trend_df)

    # ---------- DISPLAY ----------
    st.markdown("## 📋 Decision Trace")
    display_cols = ["flavor", "trend_score", "sentiment_score", "brand_fit_score",
                     "signal_quality_score", "final_score", "decision", "reason"]
    st.dataframe(trace_df[display_cols], use_container_width=True)

    st.markdown("## 🏆 Golden Candidate")
    accepted = trace_df[trace_df["decision"] == "ACCEPT"]

    if accepted.empty:
        st.error("❌ No flavour met acceptance criteria.")
    else:
        top = accepted.iloc[0]
        st.success(f"🚀 {top['flavor']} (Score: {top['final_score']})")