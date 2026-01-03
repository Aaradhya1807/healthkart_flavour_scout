import streamlit as st
import pandas as pd
import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# -------------------- CONFIG --------------------
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="Flavor Scout Engine", layout="wide")

# -------------------- HEADER --------------------
st.title("🍽️ Flavor Scout Engine")
st.subheader("AI-Powered Flavor Discovery for HealthKart")

# -------------------- DECISION PIPELINE --------------------
st.markdown("## 🧠 How Flavor Decisions Are Made")

with st.expander("Click to understand the end-to-end decision logic"):
    st.markdown("""
### Flavor Scout follows a **5-step decision pipeline**:

**1️⃣ Social Data Ingestion**  
User comments from social platforms are used as raw market signals.

**2️⃣ Signal Cleaning & Extraction**  
Duplicate, vague, or irrelevant chatter is ignored. Only meaningful flavor mentions are considered.

**3️⃣ Trend Strength Estimation**  
Mentions are counted to identify early demand signals (frequency + context).

**4️⃣ LLM-based Reasoning Engine**  
An LLM evaluates each flavor on:
- Trend strength  
- Sentiment & excitement  
- Brand alignment (MuscleBlaze / HK Vitals)  
- Noise vs signal quality  

**5️⃣ Decision Output**
- ✅ Accepted flavors (with scores & confidence)  
- ❌ Rejected flavors (with clear reasons)  
- ⭐ One *Golden Candidate* recommended for business action
""")

# -------------------- LOAD DATA --------------------
df = pd.read_csv("data/social_chatter.csv")

st.markdown("## 💬 Social Media Chatter")
st.write(f"Loaded **{len(df)}** comments")
st.dataframe(df, use_container_width=True)

# -------------------- TREND WALL --------------------
st.markdown("## 📊 Trend Signals (Explainable)")

all_text = " ".join(df["comment"].tolist()).lower()

keywords = [
    "chocolate", "vanilla", "kesar", "pista", "chai",
    "watermelon", "blueberry", "cocoa", "nimbu", "orange"
]

trend_counts = {k: all_text.count(k) for k in keywords}

trend_df = pd.DataFrame({
    "Flavor": trend_counts.keys(),
    "Mentions": trend_counts.values()
}).sort_values(by="Mentions", ascending=False)

st.bar_chart(trend_df.set_index("Flavor"))

st.caption("Higher mentions indicate stronger early demand signals.")

# -------------------- AI ANALYSIS --------------------
st.markdown("## 🤖 AI Decision Engine")

if st.button("🔍 Analyze with AI"):
    comments_text = "\n".join(df["comment"].tolist())

    prompt = f"""
You are a product analyst at HealthKart.

TASK:
Evaluate flavor ideas from social media comments using a **structured decision framework**.

DECISION CRITERIA:
- Trend strength (frequency + excitement)
- Sentiment positivity
- Brand alignment (MuscleBlaze / HK Vitals)
- Signal vs noise quality

INSTRUCTIONS:
- Be conservative and realistic
- Scores above 80 should be rare
- Reject weak or irrelevant ideas clearly

OUTPUT:
Return ONLY valid JSON. Do NOT include markdown or explanations.

FORMAT:
{{
  "selected": [
    {{
      "flavor": "",
      "brand": "",
      "trend_score": 0,
      "confidence": "High / Medium / Low",
      "why": ""
    }}
  ],
  "rejected": [
    {{
      "flavor": "",
      "reason": ""
    }}
  ],
  "golden_candidate": {{
    "flavor": "",
    "brand": "",
    "trend_score": 0,
    "confidence": "",
    "why": ""
  }}
}}

COMMENTS:
{comments_text}
"""

    with st.spinner("AI is evaluating flavor decisions..."):
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )

    raw_output = response.choices[0].message.content.strip()

    # -------------------- JSON SANITIZATION --------------------
    if raw_output.startswith("```"):
        raw_output = raw_output.replace("```json", "")
        raw_output = raw_output.replace("```", "")
        raw_output = raw_output.strip()

    st.markdown("### 🧾 Raw AI Output (Debug)")
    st.code(raw_output, language="json")

    try:
        ai_output = json.loads(raw_output)
    except json.JSONDecodeError:
        st.error("⚠️ AI output could not be parsed as JSON.")
        st.stop()

    # -------------------- DECISION OUTPUT --------------------
    st.markdown("## 🧠 Decision Results")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### ✅ Accepted Ideas")
        for item in ai_output["selected"]:
            st.success(
                f"""
**{item['flavor']}** — *{item['brand']}*  
**Trend Score:** {item['trend_score']}  
**Confidence:** {item['confidence']}  

{item['why']}
"""
            )

    with col2:
        st.markdown("### ❌ Rejected Ideas")
        for item in ai_output["rejected"]:
            st.error(
                f"**{item['flavor']}** — {item['reason']}"
            )

    # -------------------- GOLDEN CANDIDATE --------------------
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
    <p><strong>Trend Score:</strong> {gc['trend_score']} | <strong>Confidence:</strong> {gc['confidence']}</p>
    <p style="font-size:18px;">{gc['why']}</p>
</div>
""",
        unsafe_allow_html=True
    )
