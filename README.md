# 🍽️ Flavor Scout Engine

AI-powered flavor discovery platform built as part of the **HealthKart Product Analytics Assignment**. The application analyzes social media chatter to identify emerging flavor trends, filter weak ideas, and recommend a **Golden Candidate** aligned with HealthKart brands.

---

## 🚀 Live Demo

🔗 **Live App:** [https://healthkart-flavour-scout.onrender.com](https://healthkart-flavour-scout.onrender.com)

🔗 **GitHub Repository:** [https://github.com/Aaradhya1807/healthkart_flavour_scout](https://github.com/Aaradhya1807/healthkart_flavour_scout)

---

## 🎯 Problem Statement

Flavor innovation in nutrition products is often reactive and intuition-driven. By the time trends appear in sales data, the opportunity window may already be closing.

**Flavor Scout Engine** addresses this gap by:

* Listening to unstructured consumer conversations
* Identifying early demand signals
* Translating noisy social chatter into clear product insights

---

## 🧠 Solution Overview

Flavor Scout Engine uses **AI-driven reasoning** to:

* Extract potential flavor ideas from social media comments
* Filter out weak, noisy, or misaligned ideas
* Evaluate brand-fit across HealthKart portfolios
* Highlight the strongest recommendation as a **Golden Candidate**

The output is designed for **business users**, not just data scientists.

---

## 🏗️ Architecture

```
Social Chatter (CSV)
        ↓
Data Preprocessing (Pandas)
        ↓
AI Reasoning Engine (OpenAI API)
        ↓
Decision Engine
  ├── Selected Ideas
  ├── Rejected Ideas
  └── Golden Candidate
        ↓
Streamlit Dashboard (UI)
```

---

## 📊 Key Features

* 📥 **Social Chatter Ingestion** – Simulated Reddit/review data
* 🤖 **AI-Powered Reasoning** – Structured JSON-based outputs
* 🧩 **Decision Engine** – Clear separation of selected vs rejected ideas
* 🏆 **Golden Candidate Highlight** – Single strongest recommendation
* 🔐 **Secure Deployment** – Secrets managed via environment variables

---

## 🧪 Example Output

**Selected Ideas**

* Masala Chai (MuscleBlaze) – Appeals to Indian palate with post-workout positioning
* Dark Cocoa (MuscleBlaze) – Targets users preferring low sweetness
* Watermelon (HK Vitals) – Refreshing wellness-focused option

**Golden Candidate**

* **Masala Chai Whey – MuscleBlaze**

---

## ⚙️ Tech Stack

* **Frontend / UI:** Streamlit
* **Backend / Logic:** Python
* **AI Engine:** OpenAI API
* **Data Processing:** Pandas
* **Deployment:** Render
* **Version Control:** Git & GitHub

---

## 🔐 Environment Variables

The application requires the following environment variable:

```
OPENAI_API_KEY=your_api_key_here
```

> ⚠️ API keys are never committed to the repository and are injected securely at deployment time.

---

## 🛠️ Local Setup

```bash
# Clone the repository
git clone https://github.com/Aaradhya1807/healthkart_flavour_scout.git
cd healthkart_flavour_scout

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

---

## 📈 Future Enhancements

* Live Reddit / Twitter API integration
* Trend momentum scoring over time
* Category-level insights (protein, wellness, hydration)
* Exportable reports for product teams

---

## 👤 Author

**Aaradhya Maharishi**
Aspiring Data Analyst / Product Analyst
Built as part of HealthKart Internship Assignment

---

## 📝 Note

This project focuses on **decision intelligence**, not just text summarization. The goal is to help product teams move from intuition-based decisions to **evidence-backed flavor innovation**.
