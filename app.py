import streamlit as st
import pandas as pd
import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# ------------------ SETUP ------------------
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="Flavor Scout", layout="wide")
st.title("🍽️ Flavor Scout Engine")

# ------------------ DECISION PIPELINE ------------------
st.markdown("## 🧠 How Flavor Decisions Are Made")

with st.expander("Click to understand the decision pipeline"):
    st.markdown("""
    **Flavor Scout follows a structured, explainable decision pipeline:**

    **1️⃣ Social Media Data Collection**  
    Raw comments from social platforms are used as input signals.

    **2️⃣ Cleaning & Signal Extraction**  
    Irrelevant chatter and noise are reduced to focus on meaningful flavor mentions.

    **3️⃣ Trend Detection**  
    Frequency and context of mentions are analyzed to assess emerging interest.

    **4️⃣ LLM-based Decision Engine**  
    Each flavor is evaluated using fixed criteria:
    - Trend Strength  
    - Consumer Sentiment  
    - Brand Fit (MuscleBlaze / HK Vitals)  
    - Noise vs Signal Quality  

    **5️⃣ Decision Output**
    - ✅ Accepted flavors with reasons  
    - ❌ Rejected flavors with clear justification  
    - ⭐ One Golden Candidate for product consideration
    """)

st.subheader("AI-Powered Flavor Discovery for HealthKart")

# ------------------ LOAD DATA ------------------
df = pd.read_csv("data/social_chatter.csv")

st.markdown("### 💬 Social Media Chatter")
st.write(f"Loaded **{len(df)}** social comments")
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
    "Flavor Keyword": trend_data.keys(),
    "Mentions": trend_data.values()
}).sort_values(by="Mentions", ascending=False)

st.bar_chart(trend_df.set_index("Flavor Keyword"))

# ------------------ DECISION CRITERIA ------------------
DECISION_CRITERIA = """
Decision Criteria:

1. Trend Strength:
   - High: Frequently mentioned
   - Medium: Moderate mentions
   - Low: Rare mentions

2. Sentiment:
   - Positive: Excitement, liking, demand
   - Neutral: Casual mentions
   - Negative: Dislike or rejection

3. Brand Fit:
   - MuscleBlaze: Performance, gym-centric flavors
   - HK Vitals: Wellness, refreshment, lifestyle flavors

4. Noise Level:
   - Low: Clear, relevant context
   - High: Spam or irrelevant chatter
"""

# ------------------ AI ANALYSIS ------------------
st.markdown("## 🤖 AI Analysis")

if st.button("🔍 Analyze with AI"):
    comments_text = "\n".join(df["comment"].tolist())

    prompt = f"""
You are a product analyst at HealthKart.

Your task is to make clear ACCEPT or REJECT decisions for potential
flavor ideas using ONLY the criteria below:

{DECISION_CRITERIA}

Instructions:
1. Extract potential flavor ideas from the comments.
2. For EACH flavor:
   - Decide ACCEPT or REJECT
   - Clearly explain which criteria passed or failed
3. ACCEPT only the TOP 3 strongest flavors.
4. From accepted flavors, choose ONE Golden Candidate.

Return STRICT JSON only in this format:

{{
  "accepted": [
    {{
      "flavor": "",
      "brand": "",
      "reason": ""
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
    "reason": ""
  }}
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

    try:
        ai_output = json.loads(raw_output)
    except json.JSONDecodeError:
        st.error("⚠️ AI output could not be parsed as JSON.")
        st.code(raw_output)
        st.stop()

    # ------------------ RESULTS UI ------------------
    st.markdown("## 🧠 Decision Results")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### ✅ Accepted Flavor Ideas")
        for item in ai_output["accepted"]:
            st.success(f"**{item['flavor']}** ({item['brand']})\n\n{item['reason']}")

    with col2:
        st.markdown("### ❌ Rejected Flavor Ideas")
        for item in ai_output["rejected"]:
            st.error(f"**{item['flavor']}** — {item['reason']}")

    st.markdown("## ⭐ Golden Candidate")

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
            <p style="font-size:18px;">{gc['reason']}</p>
        </div>
        """,
        unsafe_allow_html=True
    )
