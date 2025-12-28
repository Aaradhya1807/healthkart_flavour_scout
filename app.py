import streamlit as st
import pandas as pd
import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Page config
st.set_page_config(page_title="Flavor Scout", layout="wide")
st.title("🍽️ Flavor Scout Engine")
st.subheader("AI-Powered Flavor Discovery for HealthKart")

# -----------------------------
# Load social chatter data
# -----------------------------
df = pd.read_csv("data/social_chatter.csv")

st.markdown("### 💬 Social Media Chatter")
st.write(f"Loaded **{len(df)}** social comments")
st.dataframe(df, use_container_width=True)

# -----------------------------
# Trend Wall
# -----------------------------
st.markdown("## 📊 Trend Wall")

all_text = " ".join(df["comment"].tolist()).lower()
keywords = [
    "chocolate", "vanilla", "kesar", "pista", "chai",
    "watermelon", "blueberry", "cocoa", "nimbu", "orange"
]

trend_data = {k: all_text.count(k) for k in keywords}

trend_df = pd.DataFrame({
    "Flavor Keyword": trend_data.keys(),
    "Mentions": trend_data.values()
}).sort_values(by="Mentions", ascending=False)

st.bar_chart(trend_df.set_index("Flavor Keyword"))

# -----------------------------
# AI Analysis
# -----------------------------
st.markdown("## 🤖 AI Analysis")

if st.button("🔍 Analyze with AI"):
    comments_text = "\n".join(df["comment"].tolist())

    prompt = f"""
You are a product analyst at HealthKart.

Analyze the following social media comments.

Tasks:
1. Extract flavor ideas.
2. Classify them into SELECTED or REJECTED.
3. Choose ONE Golden Candidate.
4. Give 1 simple business-friendly reason for each selected idea.
5. Ensure brand fit:
   - MuscleBlaze = Hardcore gym / performance
   - HK Vitals = Wellness / lifestyle
   - TrueBasics = Clean daily nutrition

IMPORTANT:
- Respond with ONLY valid JSON
- Do NOT add explanations
- Do NOT use markdown
- Do NOT wrap in ``` blocks

Return JSON in this exact structure:

{{
  "selected": [
    {{"flavor": "", "brand": "", "why": ""}}
  ],
  "rejected": [
    {{"flavor": "", "reason": ""}}
  ],
  "golden_candidate": {{"flavor": "", "brand": "", "why": ""}}
}}

Comments:
{comments_text}
"""

    with st.spinner("AI is analyzing social chatter..."):
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )

    raw_output = response.choices[0].message.content.strip()

    # Debug view (optional but useful)
    st.markdown("### 🧾 Raw AI Output (Debug)")
    st.code(raw_output, language="json")

    try:
        ai_output = json.loads(raw_output)
    except json.JSONDecodeError:
        st.error("⚠️ AI output could not be parsed as JSON.")
        st.stop()

    # -----------------------------
    # Decision Engine
    # -----------------------------
    st.markdown("## 🧠 Decision Engine")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### ✅ Selected Ideas")
        for item in ai_output["selected"]:
            st.success(
                f"**{item['flavor']}** ({item['brand']})\n\n{item['why']}"
            )

    with col2:
        st.markdown("### ❌ Rejected Ideas")
        for item in ai_output["rejected"]:
            st.error(
                f"**{item['flavor']}** — {item['reason']}"
            )

    # -----------------------------
    # Golden Candidate
    # -----------------------------
    st.markdown("## 🏆 Golden Candidate")

    gc = ai_output["golden_candidate"]

    st.markdown(
        f"""
        <div style="
            padding: 30px;
            border-radius: 15px;
            background-color: #0f172a;
            color: white;
        ">
            <h2>🚀 {gc['flavor']} — {gc['brand']}</h2>
            <p style="font-size:18px;">{gc['why']}</p>
        </div>
        """,
        unsafe_allow_html=True
    )
