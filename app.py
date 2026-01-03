import streamlit as st
import pandas as pd
import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# ------------------ SETUP ------------------
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="Flavor Scout Engine", layout="wide")

st.title("🍽️ Flavor Scout Engine")
st.subheader("AI-Powered Flavor Discovery for HealthKart")

# ------------------ EXPLAINABILITY ------------------
st.markdown("## 🧠 How Flavor Decisions Are Made")

with st.expander("Click to understand the decision pipeline"):
    st.markdown("""
**Flavor Scout follows an explainable decision pipeline:**

1️⃣ **Data Collection**  
Social media comments are collected as raw, unstructured input.

2️⃣ **Signal Extraction**  
Noise and irrelevant chatter are reduced to capture genuine flavor demand.

3️⃣ **Trend & Sentiment Analysis**  
Mentions are evaluated based on frequency, excitement, and context.

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
df = pd.read_csv("data/social_chatter.csv")

st.markdown("### 💬 Social Media Chatter")
st.write(f"Loaded **{len(df)}** comments")
st.dataframe(df, use_container_width=True)

# ------------------ TREND WALL ------------------
st.markdown("## 📊 Trend Wall")

all_text = " ".join(df["comment"].tolist()).lower()

keywords = [
    "chocolate", "vanilla", "kesar", "pista", "chai",
    "watermelon", "blueberry", "cocoa", "nimbu", "orange"
]

trend_data = {k: all_text.count(k) for k in keywords}

trend_df = pd.DataFrame({
    "Flavor": trend_data.keys(),
    "Mentions": trend_data.values()
}).sort_values(by="Mentions", ascending=False)

st.bar_chart(trend_df.set_index("Flavor"))

# ------------------ AI ANALYSIS ------------------
st.markdown("## 🤖 AI Decision Engine")

if st.button("🔍 Analyze with AI"):

    comments_text = "\n".join(df["comment"].tolist())

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

    # ------------------ RAW OUTPUT ------------------
    raw_output = response.choices[0].message.content.strip()

    # ------------------ CLEAN OUTPUT (CRITICAL FIX) ------------------
    if raw_output.startswith("```"):
        raw_output = raw_output.replace("```json", "")
        raw_output = raw_output.replace("```", "")
        raw_output = raw_output.strip()

    if "{" in raw_output and "}" in raw_output:
        raw_output = raw_output[
            raw_output.find("{"): raw_output.rfind("}") + 1
        ]

    st.markdown("### 🧾 Raw AI Output (Debug)")
    st.code(raw_output, language="json")

    # ------------------ PARSE JSON ------------------
    try:
        ai_output = json.loads(raw_output)
    except json.JSONDecodeError:
        st.error("⚠️ AI output could not be parsed as JSON.")
        st.stop()

    # ------------------ DECISION TRACE ------------------
    st.markdown("## 📋 Decision Trace (Explainable Scoring)")

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

    # ------------------ ACCEPT / REJECT ------------------
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
