# 🍽️ Flavor Scout Engine  
## AI-Driven Flavor Decision System for HealthKart

Flavor Scout Engine is an **explainable product decision system** built as part of the **HealthKart Product Analytics Assignment**.  
The platform converts noisy social media chatter into **clear, auditable flavor decisions** using structured analytics and LLM-based reasoning.

---

## 🚀 Live Demo & Code

🔗 **Live App:** https://healthkart-flavour-scout.onrender.com  
🔗 **GitHub Repo:** https://github.com/Aaradhya1807/healthkart_flavour_scout  

---

## 🎯 Business Problem

Flavor innovation in nutrition products often relies on intuition or delayed sales data.  
By the time trends appear in dashboards, **consumer interest may already be fading**.

HealthKart needs a system that can:

- Listen to **early consumer conversations**
- Separate **signal from noise**
- Clearly explain **why a flavor is accepted or rejected**
- Recommend **one high-confidence flavor** for business action

---

## 🧠 Solution Overview

Flavor Scout Engine acts as a **Decision Intelligence Layer** between social chatter and product teams.

It does **not** merely summarize comments — it **reasons about them**.

The system outputs:
- ✅ Accepted flavor ideas (with scores + reasoning)
- ❌ Rejected ideas (with clear rejection logic)
- 🏆 One **Golden Candidate** recommended for launch consideration

---

## 🔍 Decision Pipeline (End-to-End)

### 1️⃣ Social Media Data Collection
- Input data simulates Reddit / review / comment-based chatter  
- Stored as a structured CSV (`social_chatter.csv`)

---

### 2️⃣ Signal Extraction & Trend Detection
- Flavor keywords are identified
- Mention frequency and context are evaluated
- High-noise, low-intent chatter is deprioritized

---

### 3️⃣ Explainable Scoring Engine (Core Logic)

Each flavor is evaluated on **four independent dimensions (0–100):**

| Score Type | Description |
|----------|------------|
| **Trend Score** | Frequency and momentum of mentions |
| **Sentiment Score** | Positive vs neutral vs negative consumer tone |
| **Brand Fit Score** | Alignment with HealthKart brands (MuscleBlaze, HK Vitals, etc.) |
| **Signal Quality Score** | Noise vs genuine, repeated consumer intent |

**Final Score Calculation:**
Final Score = Average of all four scores

---

### 4️⃣ Acceptance & Rejection Logic (Decision Criteria)

Flavor Scout uses **explicit, quantitative rules** — not subjective AI opinions.

- **Final Score ≥ 75 → ACCEPT**  
  Indicates strong, high-confidence demand suitable for product consideration

- **Final Score < 75 → REJECT**  
  Indicates weak signal, low confidence, or insufficient brand alignment

This conservative threshold reflects **real-world product launch risk**, ensuring that only
high-quality, defensible ideas move forward.

Each decision is accompanied by a **business-friendly explanation**.

---

### 5️⃣ LLM-Based Decision Reasoning
A Large Language Model acts as a **Product Analyst**, using the computed scores to:

- ACCEPT strong flavor ideas
- REJECT weak or noisy ideas (with reasons)
- Justify each decision in clear business language

The LLM returns **strict structured JSON**, enabling transparency and auditability.

---

### 6️⃣ Golden Candidate Selection
The system selects **one** flavor with:
- Highest final score
- Strong brand alignment
- Clear launch justification

This mirrors how **real product councils and leadership reviews operate**.

---

## 📊 Output Example

### ✅ Accepted Flavors
- **Masala Chai — MuscleBlaze**  
  High cultural relevance, frequent mentions, and strong post-workout positioning

- **Nimbu Pani — HK Vitals**  
  Refreshing wellness association with hydration use-cases

---

### ❌ Rejected Flavors
- Low mention frequency  
- Ambiguous sentiment  
- Weak product-market fit  

Each rejection includes a **clear explanation**.

---

### 🏆 Golden Candidate
**Masala Chai Whey — MuscleBlaze**  
Strong trend momentum, emotional recall, and brand synergy for Indian fitness consumers.

---

## 🖥️ Dashboard Highlights

- 📋 **Decision Trace Table** (Explainable Scoring)
- 🧠 **Accept vs Reject Breakdown**
- 🏆 **Golden Candidate Recommendation Card**
- 🔍 **Raw AI Output Debug Panel** (for transparency)

Designed for **Product Managers and Business Teams**, not just engineers.

---

## ⚙️ Tech Stack

- **Frontend:** Streamlit  
- **Backend:** Python  
- **Data Processing:** Pandas  
- **AI Reasoning:** OpenAI API (LLM)  
- **Deployment:** Render  
- **Version Control:** Git & GitHub  

---

## 🔐 Environment Variables


---

### 4️⃣ Acceptance & Rejection Logic (Decision Criteria)

Flavor Scout uses **explicit, quantitative rules** — not subjective AI opinions.

- **Final Score ≥ 75 → ACCEPT**  
  Indicates strong, high-confidence demand suitable for product consideration

- **Final Score < 75 → REJECT**  
  Indicates weak signal, low confidence, or insufficient brand alignment

This conservative threshold reflects **real-world product launch risk**, ensuring that only
high-quality, defensible ideas move forward.

Each decision is accompanied by a **business-friendly explanation**.

---

### 5️⃣ LLM-Based Decision Reasoning
A Large Language Model acts as a **Product Analyst**, using the computed scores to:

- ACCEPT strong flavor ideas
- REJECT weak or noisy ideas (with reasons)
- Justify each decision in clear business language

The LLM returns **strict structured JSON**, enabling transparency and auditability.

---

### 6️⃣ Golden Candidate Selection
The system selects **one** flavor with:
- Highest final score
- Strong brand alignment
- Clear launch justification

This mirrors how **real product councils and leadership reviews operate**.

---

## 📊 Output Example

### ✅ Accepted Flavors
- **Masala Chai — MuscleBlaze**  
  High cultural relevance, frequent mentions, and strong post-workout positioning

- **Nimbu Pani — HK Vitals**  
  Refreshing wellness association with hydration use-cases

---

### ❌ Rejected Flavors
- Low mention frequency  
- Ambiguous sentiment  
- Weak product-market fit  

Each rejection includes a **clear explanation**.

---

### 🏆 Golden Candidate
**Masala Chai Whey — MuscleBlaze**  
Strong trend momentum, emotional recall, and brand synergy for Indian fitness consumers.

---

## 🖥️ Dashboard Highlights

- 📋 **Decision Trace Table** (Explainable Scoring)
- 🧠 **Accept vs Reject Breakdown**
- 🏆 **Golden Candidate Recommendation Card**
- 🔍 **Raw AI Output Debug Panel** (for transparency)

Designed for **Product Managers and Business Teams**, not just engineers.

---

## ⚙️ Tech Stack

- **Frontend:** Streamlit  
- **Backend:** Python  
- **Data Processing:** Pandas  
- **AI Reasoning:** OpenAI API (LLM)  
- **Deployment:** Render  
- **Version Control:** Git & GitHub  

---

## 🔐 Environment Variables

OPENAI_API_KEY=your_api_key_here


API keys are **never committed to GitHub** and are securely injected at deployment.

---

## 🛠️ Local Setup

```bash
git clone https://github.com/Aaradhya1807/healthkart_flavour_scout.git
cd healthkart_flavour_scout

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

## 📈 Future Enhancements

Live Reddit / Twitter ingestion

Time-series trend momentum tracking

Category-level recommendations (Protein, Wellness, Hydration)

Exportable, product-ready decision reports

## 👤 Author

Aaradhya Maharishi
Aspiring Data / Product Analyst

Built as part of a HealthKart Product Analytics Assignment, with a strong focus on
explainable decision intelligence, not just dashboards.