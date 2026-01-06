# 🍽️ Flavor Scout Engine
AI-Driven Flavor Decision System for HealthKart

Flavor Scout Engine is an explainable product decision system built as part of the HealthKart Product Analytics Assignment.

The platform converts noisy, unstructured social media chatter into clear, auditable flavor decisions using structured analytics and LLM-based reasoning — focusing on decision intelligence, not just insights.

# 🚀 Live Demo & Code

## 🔗 Live App: https://healthkart-flavour-scout.onrender.com

## 🔗 GitHub Repo: https://github.com/Aaradhya1807/healthkart_flavour_scout

# 🎯 Business Problem

Flavor innovation in nutrition products often relies on intuition or delayed sales data.
By the time trends appear in dashboards, consumer interest may already be fading.

HealthKart needs a system that can:

Listen to early consumer conversations

Separate signal from noise

Clearly explain why a flavor is accepted or rejected

Recommend one high-confidence flavor for business action

# 🧠 Solution Overview

Flavor Scout Engine acts as a Decision Intelligence Layer between social chatter and product teams.

It does not just summarize comments — it reasons about them.

The system outputs:

✅ Accepted flavor ideas (with scores + reasoning)

❌ Rejected ideas (with rejection logic)

🏆 One Golden Candidate recommended for launch consideration

🔍 Decision Pipeline (End-to-End)
1️⃣ Social Media Data Collection

Input data simulates Reddit / review / comment-based chatter

Stored as structured CSV (social_chatter.csv)

Supports live Reddit ingestion (beta) with graceful fallback

2️⃣ Signal Extraction & Trend Detection

Flavor keywords are identified

Mention frequency is calculated

High-noise, low-intent chatter is deprioritized

3️⃣ Explainable Scoring Engine (Core Logic)

Each flavor is evaluated on four independent dimensions:

Score Type	Description
Trend Score	Frequency and strength of mentions
Sentiment Score	Positive vs neutral vs negative context
Brand Fit Score	Alignment with HealthKart brands (MuscleBlaze, HK Vitals, etc.)
Signal Quality Score	Noise vs genuine consumer intent

A Final Score (0–100) is computed using weighted reasoning.

# 🎯 Final Acceptance Logic

Decision Rules:

✅ ACCEPT → Final Score ≥ 75 (High confidence, launch-worthy)

❌ REJECT → Final Score < 75 (Weak signal or high noise)

This threshold-based logic mirrors real-world product council decisions, ensuring only strong, defensible ideas move forward.

4️⃣ LLM-Based Decision Reasoning

A Large Language Model acts as a Product Analyst, using the scores to:

Accept strong flavor ideas

Reject weak or noisy ideas (with clear reasons)

Justify decisions in business-readable language

The LLM returns strict structured JSON, enabling transparency and auditability.

5️⃣ Golden Candidate Selection

The system selects one flavor with:

Highest final score

Strong brand alignment

Clear launch justification

This mirrors how real product councils prioritize ideas.

## 📊 Output Example
✅ Accepted Flavors

Masala Chai — MuscleBlaze
Strong cultural relevance, frequent mentions, post-workout appeal

Nimbu Pani — HK Vitals
Refreshing hydration use-case with positive wellness sentiment

❌ Rejected Flavors

Low mention frequency

Ambiguous sentiment

Weak product-market fit

Each rejection includes a clear explanation.

## 🏆 Golden Candidate

Masala Chai Whey — MuscleBlaze
High trend momentum, emotional recall, and strong brand synergy for Indian fitness consumers.

# 🖥️ Dashboard Highlights

📋 Decision Trace Table (Explainable Scoring)

🧠 Accept vs Reject Breakdown

🏆 Golden Candidate Card

## 🔍 Raw AI Output Debug Panel (Transparency)

Designed for Product Managers, not just engineers.

# ⚙️ Tech Stack

Frontend: Streamlit

Backend: Python

Data Processing: Pandas

AI Reasoning: OpenAI API (LLMs)

Deployment: Render

Version Control: Git & GitHub

# 🔐 Environment Variables

OPENAI_API_KEY=your_api_key_here
API keys are never committed to GitHub and are securely injected at deployment.

# 🛠️ Local Setup

git clone https://github.com/Aaradhya1807/healthkart_flavour_scout.git
cd healthkart_flavour_scout

python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py


# 📈 Future Enhancements

Live Reddit / Twitter ingestion (full-scale)

Time-series trend momentum tracking

Category-level recommendations (Protein, Wellness, Hydration)

Exportable, product-ready decision reports

## 👤 Author

Aaradhya Maharishi
Aspiring Data & Product Analyst

Built as part of a HealthKart Product Analytics Assignment, with a focus on explainable decision intelligence, not black-box AI.