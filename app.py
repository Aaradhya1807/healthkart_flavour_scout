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
INTENT_THRESHOLD = int((1 - INTENT_STRICTNESS) * 100)  # 25

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
    keyword = st.text_input("Enter keyword / topic to analyze", value="whey protein")

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
            max_videos=10,
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

    # ---------- DOMAIN GATE ----------
    FLAVOUR_CONTEXT_KEYWORDS = [
        "flavour", "flavor", "taste", "tasty", "sweet", "sour",
        "chocolate", "vanilla", "strawberry", "mango", "mint",
        "cookie", "banana", "whey", "protein", "shake",
        "ice cream", "drink"
    ]

    comments_lower = comments_text.lower()

    if not any(word in comments_lower for word in FLAVOUR_CONTEXT_KEYWORDS):
        st.warning("⚠️ No flavours detected in comments.")
        st.stop()


    # ---------- PROMPT ----------
    prompt = f"""
You are a flavour extraction engine.

IMPORTANT RULES (STRICT):
- Output ONLY raw, valid JSON
- Do NOT include explanations
- Do NOT include markdown
- Do NOT include python code
- Do NOT include variables, loops, functions, or logic
- All values must be literal strings or numbers
- Do NOT invent flavours

DEFINITION:
A flavour is ONLY a concrete, edible or consumable sensory variant.
Examples: vanilla, chocolate, strawberry, mango mint, cookie blast.

INVALID (DO NOT SELECT AS FLAVOURS):
- Brands or company names
- Product categories
- Mobile, tech, or electronic terms
- Awareness, education, or health topics
- Abstract concepts
- Colours unless they are edible flavours

CRITICAL RULE:
If the comments do NOT clearly discuss food, beverages, supplements,
or consumable flavour contexts, return an EMPTY decision_trace.

If NO valid flavours are found, return EXACTLY this JSON:

{{
  "decision_trace": []
}}

OUTPUT FORMAT (STRICT — DO NOT DEVIATE):

{{
  "decision_trace": [
    {{
      "flavor": "vanilla",
      "trend_score": 82,
      "signal_quality_score": 78,
      "final_score": 80
    }}
  ]
}}

COMMENTS:
{comments_text}
"""


    with st.spinner("AI is analyzing flavour signals..."):
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

    # ---------- SAFE JSON EXTRACTION ----------
    start = raw_output.find("{")
    end = raw_output.rfind("}")

    if start == -1 or end == -1:
        st.warning("⚠️ No flavours detected in comments.")
        st.stop()

    cleaned = raw_output[start:end + 1]

    try:
        ai_output = json.loads(cleaned)
    except json.JSONDecodeError:
        st.error("❌ AI returned invalid JSON")
        st.code(cleaned)
        st.stop()

    decision_trace = ai_output.get("decision_trace", [])

    if not decision_trace:
        st.warning("⚠️ No flavours detected in comments.")
        st.stop()

    # ---------- DECISION TRACE ----------
    trace_df = pd.DataFrame(decision_trace)

    required_cols = {"flavor", "trend_score", "signal_quality_score", "final_score"}
    if trace_df.empty or not required_cols.issubset(trace_df.columns):
        st.warning("⚠️ No valid flavour intent detected.")
        st.stop()

    # ---------- HARD FLAVOUR VALIDATION ----------
    INVALID_KEYWORDS = [
        "awareness", "education", "health", "guidance",
        "company", "brand", "campaign", "initiative"
    ]

    def is_valid_flavour(flavour):
        flavour = flavour.lower()
        if len(flavour.split()) > 3:
            return False
        return not any(word in flavour for word in INVALID_KEYWORDS)

    trace_df = trace_df[trace_df["flavor"].apply(is_valid_flavour)]

    if trace_df.empty:
        st.warning("⚠️ No flavours detected in comments.")
        st.stop()

    # ---------- FILTER LOW INTENT ----------
    trace_df = trace_df[
        (trace_df["trend_score"] > 0) |
        (trace_df["signal_quality_score"] >= INTENT_THRESHOLD)
    ]

    if trace_df.empty:
        st.warning("⚠️ No flavours found with meaningful intent.")
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

    # ---------- BUSINESS RULE ----------
    trace_df["decision"] = trace_df["final_score"].apply(
        lambda x: "ACCEPT" if x >= ACCEPT_THRESHOLD else "REJECT"
    )

    # ---------- INTENT-BASED REASON ----------
    def intent_reason(row):
        if row["final_score"] >= ACCEPT_THRESHOLD:
            return "Strong positive sentiment and repeated favourable mentions."
        return "Negative or weak sentiment observed across user comments."

    trace_df["reason"] = trace_df.apply(intent_reason, axis=1)

    # ---------- DISPLAY ----------
    st.markdown("## 📋 Decision Trace")
    st.dataframe(trace_df, use_container_width=True)

    st.markdown("## 📊 Trend Wall")
    st.bar_chart(trace_df.set_index("flavor")["trend_score"])

    st.markdown("## 🏆 Golden Candidate Recommendation")

    accepted_df = trace_df[trace_df["decision"] == "ACCEPT"]

    if accepted_df.empty:
        st.error("❌ No flavour met acceptance criteria.")
    else:
        golden = accepted_df.sort_values("final_score", ascending=False).iloc[0]
        st.success(
            f"🚀 Golden Candidate: **{golden['flavor']}** "
            f"(Score: {golden['final_score']})"
        )
