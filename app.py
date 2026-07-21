import streamlit as st
import pandas as pd
import os
import json
from dotenv import load_dotenv
from groq import Groq

from reddit_ingest import fetch_reddit_comments, get_disabled_reason
from youtube_ingest import fetch_comments_by_query
from domains import PRESETS, custom_domain

# ================== SETUP ==================
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

st.set_page_config(page_title="Noise2Signal", layout="wide")

ACCEPT_THRESHOLD = 75
MAX_ITEMS = 8

# Weights for the composite score — same four components regardless of
# domain, so the framework generalizes without touching this formula.
SCORE_WEIGHTS = {
    "trend_score": 0.35,
    "sentiment_score": 0.30,
    "brand_fit_score": 0.20,
    "signal_quality_score": 0.15,
}

st.title("🔍 Noise2Signal")
st.subheader("AI-Powered Product Signal Discovery")

# ================== ANGLE SELECTION ==================
st.markdown("## 🎯 Analysis Angles")
st.caption(
    "Pick one or more angles to analyze from the same batch of comments. "
    "Each angle is scored independently (a phone model is never ranked "
    "against a camera spec — that comparison wouldn't mean anything)."
)

preset_names = st.multiselect(
    "Choose analysis angle(s)",
    options=list(PRESETS.keys()),
    default=[list(PRESETS.keys())[0]],
)

with st.expander("➕ Add a custom angle"):
    add_custom = st.checkbox("Include a custom angle in this run")
    custom_name = st.text_input("Angle name", value="Custom Angle")
    custom_item_label = st.text_input(
        "What are you extracting? (singular noun)", value="feature",
        help="e.g. 'flavor', 'spec', 'colorway', 'menu item'",
    )
    custom_description = st.text_area(
        "Describe the domain in one sentence",
        value="attributes of a product people discuss online",
    )
    custom_brand_csv = st.text_input(
        "Brand/product/accessory names to exclude (comma-separated, optional)", value="",
    )
    custom_context_csv = st.text_input(
        "A few domain keywords for a quick relevance check (comma-separated, optional)",
        value="", help="Leave blank to skip the pre-filter and let the AI judge relevance itself.",
    )

selected_domains = [(name, PRESETS[name]) for name in preset_names]
if add_custom:
    selected_domains.append((
        custom_name or "Custom Angle",
        custom_domain(custom_item_label, custom_description, custom_brand_csv, custom_context_csv),
    ))

if not selected_domains:
    st.warning("⚠️ Select at least one analysis angle above.")
    st.stop()

# ================== DECISION PIPELINE ==================
with st.expander("🔍 Click to understand the decision pipeline"):
    st.markdown(f"""
**Noise2Signal follows the same explainable pipeline for every angle:**

### 📊 Data Collection
- Social media comments are collected as raw, unstructured input — once,
  shared across all selected angles.

### 🧹 Signal Extraction (per angle)
- Each angle extracts only items matching its own definition (e.g. phone
  *models* vs. phone *specs* are extracted and scored completely separately).

### 🤖 LLM-based Scoring Engine
Each item is scored on:
- **Trend Strength** (35% weight) — how frequently and prominently it's mentioned
- **Sentiment Strength** (30% weight) — how positively people react to it
- **Brand Fit / Recommendation Strength** (20% weight) — angle-specific
- **Signal Quality** (15% weight) — how clear vs. vague/sarcastic the mentions are

Final score is a genuine weighted average of these four — not a rank-based
placeholder — so an item's score doesn't depend on what else is in the batch.

### 🛡️ Grounding Check
- Any item the AI "extracts" that doesn't actually trace back to real words
  in the comments is discarded and flagged — this catches hallucinated
  items regardless of how well the model follows instructions.

### ✅ Decision Rules
- **Final Score ≥ {ACCEPT_THRESHOLD} → ACCEPT**
- **Final Score < {ACCEPT_THRESHOLD} → REJECT**
- **One Golden Candidate per angle**
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
def load_youtube(query: str, max_videos: int, max_comments_per_video: int) -> list:
    return fetch_comments_by_query(
        query=query, max_videos=max_videos, max_comments_per_video=max_comments_per_video
    )


# ================== LOAD DATA ==================
if data_source == "Live Reddit Comments (Disabled — policy)":
    fetch_reddit_comments()
    st.info(f"{get_disabled_reason()} Showing sample data instead.")
    df = pd.read_csv("data/social_chatter.csv")

elif data_source == "Live YouTube Comments":
    default_query = selected_domains[0][1]["default_query"]
    query = st.text_input("Enter YouTube search query", value=default_query)

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


# ================== PER-ANGLE ANALYSIS ==================
def analyze_angle(angle_name, domain, comments_text, comments_lower):
    item_label = domain["item_label"]
    item_label_title = item_label[0].upper() + item_label[1:]

    st.markdown(f"---\n## 🔎 Angle: {angle_name}")

    if domain["context_keywords"] and not any(
        word in comments_lower for word in domain["context_keywords"]
    ):
        st.warning(f"⚠️ No relevant {item_label}s detected in comments for this angle.")
        return

    prompt = f"""
You are an extraction and scoring engine for the following domain:
{domain['domain_description']}

RULES:
- Output ONLY valid JSON
- No explanations, no markdown, no code
- Do NOT invent {item_label}s that aren't supported by the comments
- Return at most {MAX_ITEMS} {item_label}s

A valid {item_label} is a concrete, specific mention that actually appears
(or is clearly paraphrased) in the COMMENTS below — for example, something
in the general style of: {domain['valid_examples']}. These are illustrations
of the TYPE of thing to extract, not a list to copy — do NOT output any of
these unless it is literally discussed in the comments below.

INVALID (do not return these as {item_label}s):
{domain['invalid_examples']}

If you cannot find real evidence for at least one {item_label} in the
comments, return an empty decision_trace. An empty result is the CORRECT
output when the comments don't discuss specific {item_label}s — do not
fill in well-known examples just to have something to show.

Score each {item_label} from 0-100 on FOUR independent components based
only on evidence in the comments:
- trend_score: how frequently and prominently it's mentioned
- sentiment_score: how positively people react to it
- brand_fit_score: {domain['brand_fit_label'].lower()}
- signal_quality_score: how clear and unambiguous the mentions are (vs vague/sarcastic)

Do NOT compute a final score yourself — just return the four component
scores per {item_label}, honestly and independently of each other.

FORMAT:
{{
  "decision_trace": [
    {{
      "item": "example {item_label}",
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
        st.error(f"❌ AI request failed for '{angle_name}': {e}")
        return

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
        st.error(f"❌ AI returned invalid JSON for '{angle_name}'")
        st.code(raw_output)
        return

    decision_trace = ai_output.get("decision_trace", [])
    if not decision_trace:
        st.warning(f"⚠️ No {item_label}s detected in comments for this angle.")
        return

    trace_df = pd.DataFrame(decision_trace)
    if "item" not in trace_df.columns:
        st.error(f"❌ AI response missing 'item' field for '{angle_name}'")
        st.code(raw_output)
        return

    for col in SCORE_WEIGHTS:
        if col not in trace_df.columns:
            trace_df[col] = 50
        trace_df[col] = pd.to_numeric(trace_df[col], errors="coerce").fillna(50).clip(0, 100)

    def is_valid_item(value):
        value = str(value).lower()
        if len(value.split()) > 4:
            return False
        if any(b in value for b in domain["brand_keywords"]):
            return False
        return True

    def is_grounded(value):
        value = str(value).lower()
        if value in comments_lower:
            return True
        significant_words = [w for w in value.split() if len(w) > 3]
        if not significant_words:
            return False
        hits = sum(1 for w in significant_words if w in comments_lower)
        return hits >= max(1, len(significant_words) // 2)

    required_words = domain.get("item_must_contain_one_of") or []

    def is_on_topic(value):
        if not required_words:
            return True  # no restriction defined for this domain
        value = str(value).lower()
        return any(w in value for w in required_words)

    ungrounded = trace_df[~trace_df["item"].apply(is_grounded)]["item"].tolist()
    off_topic = trace_df[
        trace_df["item"].apply(is_grounded) & ~trace_df["item"].apply(is_on_topic)
    ]["item"].tolist()

    trace_df = trace_df[
        trace_df["item"].apply(is_valid_item)
        & trace_df["item"].apply(is_grounded)
        & trace_df["item"].apply(is_on_topic)
    ]

    if ungrounded:
        st.caption(
            f"⚠️ Discarded {len(ungrounded)} item(s) not actually traceable to the "
            f"comments (likely AI hallucination): {', '.join(ungrounded)}"
        )
    if off_topic:
        st.caption(
            f"⚠️ Discarded {len(off_topic)} item(s) that look like brand/product names "
            f"rather than a real {item_label} (category mismatch): {', '.join(off_topic)}"
        )

    if trace_df.empty:
        st.warning(f"⚠️ No valid, grounded {item_label}s detected for this angle.")
        return

    trace_df["final_score"] = sum(
        trace_df[col] * weight for col, weight in SCORE_WEIGHTS.items()
    ).round().astype(int)

    trace_df = trace_df.sort_values(by="final_score", ascending=False).reset_index(drop=True)
    trace_df = trace_df.head(MAX_ITEMS)

    trace_df["decision"] = trace_df["final_score"].apply(
        lambda x: "ACCEPT" if x >= ACCEPT_THRESHOLD else "REJECT"
    )

    def intent_reason(row):
        score = row["final_score"]
        item = row["item"]
        if score >= 95:
            return f"Overwhelmingly positive sentiment for {item}."
        elif score >= 85:
            return f"Strong positive perception for {item} with minor neutral feedback."
        elif score >= 75:
            return f"Generally liked {item_label} with some mixed opinions."
        elif score >= 60:
            return f"Mixed sentiment with noticeable criticism."
        elif score >= 40:
            return f"Predominantly negative feedback affecting appeal."
        else:
            return f"Strong negative sentiment across user comments."

    trace_df["reason"] = trace_df.apply(intent_reason, axis=1)

    st.markdown(f"#### 🔥 Trend Wall — {item_label_title} Popularity")
    trend_df = trace_df[["item", "final_score"]].set_index("item")
    st.bar_chart(trend_df)

    st.markdown("#### 📋 Decision Trace")
    display_cols = ["item", "trend_score", "sentiment_score", "brand_fit_score",
                     "signal_quality_score", "final_score", "decision", "reason"]
    st.dataframe(
        trace_df[display_cols].rename(columns={"item": item_label_title}),
        use_container_width=True,
    )

    st.markdown("#### 🏆 Golden Candidate")
    accepted = trace_df[trace_df["decision"] == "ACCEPT"]
    if accepted.empty:
        st.error(f"❌ No {item_label} met acceptance criteria for this angle.")
    else:
        top = accepted.iloc[0]
        st.success(f"🚀 {top['item']} (Score: {top['final_score']})")


st.markdown("## 🤖 AI Decision Engine")

if st.button("🔍 Analyze with AI"):
    if groq_client is None:
        st.error("❌ GROQ_API_KEY is not set. Add it to your .env file to run analysis.")
        st.stop()

    comments_text = "\n".join(df["comment"].astype(str).tolist())
    comments_lower = comments_text.lower()

    for angle_name, domain in selected_domains:
        analyze_angle(angle_name, domain, comments_text, comments_lower)