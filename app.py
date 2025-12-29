import streamlit as st
import pandas as pd
import os
import json
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


st.set_page_config(page_title="Flavor Scout", layout="wide")
st.title("🍽️ Flavor Scout Engine")
st.subheader("AI-Powered Flavor Discovery for HealthKart")


df = pd.read_csv("data/social_chatter.csv")

st.markdown("### 💬 Social Media Chatter")
st.write(f"Loaded **{len(df)}** social comments")
st.dataframe(df, use_container_width=True)


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


st.markdown("## 🤖 AI Analysis")

if st.button("🔍 Analyze with AI"):
    comments_text = "\n".join(df["comment"].tolist())

    prompt = f"""
You are a product analyst at HealthKart.

From the following social media comments, do the following:
1. Identify potential new flavor ideas.
2. Reject weak or noisy ideas.
3. Select the strongest 3 flavor ideas.
4. For each selected idea, provide:
   - trend_score (0–100 based on frequency + excitement)
   - confidence (High / Medium / Low)
   - why (1 simple business sentence)
5. Choose ONE Golden Candidate with brand suggestion and justification.

IMPORTANT:
- Be conservative and realistic.
- Scores above 80 should be rare and justified.

Comments:
{comments_text}

Return STRICT JSON only in this format:

{{
  "selected": [
    {{
      "flavor": "",
      "brand": "",
      "trend_score": 0,
      "confidence": "",
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
"""


    with st.spinner("AI is analyzing social chatter..."):
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )

    raw_output = response.choices[0].message.content.strip()

    st.markdown("### 🧾 Raw AI Output (Debug)")
    st.code(raw_output, language="json")

    try:
        ai_output = json.loads(raw_output)
    except json.JSONDecodeError:
        st.error("⚠️ AI output could not be parsed as JSON.")
        st.stop()


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
