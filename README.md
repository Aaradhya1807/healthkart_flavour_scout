# 🍽️ Flavor Scout Engine
AI-Driven Flavor Decision System for HealthKart

Flavor Scout Engine is an explainable, AI-powered product decision system designed to help nutrition brands identify high-potential flavor ideas using live consumer discussions from public platforms.

The system converts noisy social chatter into structured, auditable flavor decisions using analytics + LLM-based reasoning.

# 🚀 Live Demo & Code

## 🔗 Live App: https://healthkart-flavour-scout.onrender.com

## 🔗 GitHub Repo: https://github.com/Aaradhya1807/healthkart_flavour_scout

# 🎯 Business Problem

Flavor innovation in nutrition products often relies on intuition or delayed sales data.
By the time trends appear in dashboards, consumer interest may already be fading.

Social platforms contain early signals of flavor demand, but:

Data is noisy and unstructured

APIs are restricted or unstable

Insights are difficult to justify to stakeholders

Flavor Scout addresses this gap by providing a resilient, explainable decision pipeline.

# 🧠 Solution Overview

Flavor Scout ingests live social discussions, extracts flavor signals, and evaluates them using a transparent scoring framework.

Key capabilities:

Live social data ingestion (YouTube, Reddit)

Graceful fallback to representative sample data

Semantic trend inference (not keyword-only)

Explainable, score-based decision making

Clear ACCEPT / REJECT recommendations

# 📥 Data Sources
✅ Primary: YouTube Comments (Live)

Uses official YouTube Data API v3

Fetches comments from fitness & supplement review videos

Acts as a reliable proxy for real-time consumer sentiment

## 🧪 Secondary: Reddit (Beta)

Integrated for broader discussion coverage

Subject to API and rate-limit constraints

## 🛟 Fallback: Sample Dataset

Activated automatically when live APIs are unavailable

Ensures uninterrupted demos and analysis

This multi-source design ensures resilience, compliance, and consistent output quality.

## 🔍 Explainable Decision Pipeline

1️⃣ Data Collection
Live and cached social comments are ingested as raw input.

2️⃣ Signal Extraction
Noise is reduced to isolate meaningful flavor-related discussion.

3️⃣ Semantic Trend & Sentiment Analysis
Flavor intent is inferred from context, not just literal keyword mentions.

4️⃣ LLM-based Scoring Engine
Each flavor is scored on:

Trend Strength

Sentiment Strength

Brand Fit

Signal Quality

5️⃣ Decision Rules

Final Score ≥ 75 → ACCEPT

Final Score < 75 → REJECT

One Golden Candidate is recommended

All decisions are fully traceable.

# 📊 Trend Wall (AI-Aligned)

Instead of relying on raw keyword frequency, the Trend Wall visualizes AI-evaluated trend strength derived from the decision trace.

This avoids bias caused by:

Sparse explicit mentions

Synonyms and implicit flavor references

Trend visualization is directly aligned with the reasoning used to make product decisions.

# 📋 Decision Trace (Auditability)

Every flavor recommendation includes:

Individual component scores

Final score calculation

Clear acceptance or rejection reason

This makes the system auditable and stakeholder-friendly, suitable for real product discussions.

# 🏆 Golden Candidate

The system highlights one flavor as the Golden Candidate, representing the strongest overall opportunity based on combined signals.

# 🛠️ Tech Stack

Python

Streamlit – Interactive UI

YouTube Data API v3 – Live ingestion

Pandas – Data handling

OpenAI API – LLM-based reasoning

dotenv – Secure environment management

# 🔐 Security & Reliability

API keys are stored in environment variables

External APIs are restricted at the service level

Graceful fallback mechanisms prevent hard failures

No credentials are exposed in the repository

# 📌 Key Design Decisions

Prioritized official, compliant APIs over unstable scraping

Designed ingestion to be platform-agnostic

Focused on explainability over black-box predictions

Treated API limitations as a product constraint, not a blocker

# 🚀 Future Enhancements

Likes-weighted trend scoring

Multi-source signal blending

Time-based trend momentum tracking

Confidence intervals for recommendations

## 👤 Author

Aaradhya Maharishi
Data Analytics & Product Analytics Enthusiast

## 🧠 Final Note

Flavor Scout Engine is not a prediction system —
it is a decision-support tool built to mirror real-world product constraints and stakeholder expectations.