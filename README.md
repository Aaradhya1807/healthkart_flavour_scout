# 🔍 Noise2Signal

**AI-powered, domain-agnostic product-signal discovery from social chatter.**

Noise2Signal turns noisy, unstructured comments (YouTube, Reddit, or your own dataset) into structured, auditable "which of these should we care about?" decisions — using LLM-based extraction plus a transparent, weighted scoring framework.

It started as a single-purpose tool for HealthKart flavor discovery. It's now a **generalized framework**: the same scoring pipeline works for phone specs, sneaker colorways, cricket players, or any category you define — with zero changes to the underlying scoring logic.

> 🎥 Originally built as *Flavor Scout Engine* for HealthKart. Same core engine, now reusable across verticals.

---

## 🎯 What problem this solves

Product/feature decisions (which flavor to launch, which spec to highlight, which model to stock) often rely on intuition or lagging sales data. Social platforms carry early signal — but that signal is noisy, unstructured, and hard to justify to stakeholders with a straight face.

Noise2Signal ingests that chatter and produces:
- A ranked list of candidates, each with **four independent, LLM-scored components** (not a single opaque number)
- A clear **ACCEPT / REJECT** call per candidate, with a plain-English reason
- One **Golden Candidate** — the strongest opportunity in the batch
- A full **decision trace** — every score is traceable back to real comment text, not invented

---

## 🧠 How it works

```
1. Data Collection      → pull comments (YouTube live, or a sample CSV)
2. Angle Selection       → choose what you're looking for (a preset, or define your own)
3. Relevance Gate        → skip the batch entirely if it's obviously off-topic (saves API calls)
4. LLM Extraction        → ask the model for candidate items + 4 raw component scores
5. Grounding Filter       → discard anything not actually traceable to the real comment text
6. Vocabulary Filter      → discard anything that reads like a brand/model name, not a real item
7. Weighted Scoring       → final_score = 0.35·trend + 0.30·sentiment + 0.20·brand_fit + 0.15·signal_quality
8. Decision Trace         → ACCEPT (≥75) / REJECT (<75), with a golden candidate highlighted
```

Steps 5–6 exist because small/fast LLMs (this project uses `llama-3.1-8b-instant` via Groq for speed) will occasionally hallucinate plausible-sounding items instead of admitting "nothing here." Rather than trust the model's word, every extracted item is checked against the actual source text before it's allowed to show up as a result.

---

## 🧩 Multi-angle analysis

Real comment batches usually mix multiple types of signal at once — a phone-recommendation video's comments mention both **models** ("Moto Edge 60 Pro") and **specs** ("great camera"). Ranking those two things together would be meaningless (a camera spec isn't "better" or "worse" than a phone model — they're not the same kind of thing).

So Noise2Signal lets you pick **one or more angles** to run in a single click. Each angle:
- gets its own extraction prompt, tuned to what it's looking for
- gets its own grounding + vocabulary filters
- gets its own trend wall, decision trace, and golden candidate

They never get mixed into one ranked list.

### Built-in presets

| Preset | Extracts | Example use case |
|---|---|---|
| **HealthKart Flavors** | Flavor names | Which new protein flavor should we launch? |
| **Phone Models (Comparison)** | Specific phone model names | Which phones are people actually recommending? |
| **Phone Specs & Features** | Specs/features (camera, battery, display...) | Which features drive the most excitement? |
| **Sneaker Colorways** | Colorway/design names | Which colorway should we restock? |

### Custom angles

Don't see your category? Open **"➕ Add a custom angle"** and define:
- **Item label** — the singular noun you're extracting (e.g. `cricket player`, `menu item`, `car trim`)
- **Domain description** — one sentence describing what you're looking for
- **Brand/product names to exclude** (optional) — things that might get mentioned but aren't valid answers
- **Domain keywords** (optional) — a few words that signal "this batch is relevant" and "this candidate is legitimate," used as a lightweight relevance/vocabulary check

No code changes needed — this runs through the exact same pipeline as the built-in presets.

To make a custom angle permanent, add it to `domains.py` as a new entry in `PRESETS` (see that file's docstring for the format).

---

## 📥 Data sources

| Source | Status | Notes |
|---|---|---|
| **Sample Dataset** | ✅ Always available | `data/social_chatter.csv` — used as a fallback everywhere |
| **Live YouTube Comments** | ✅ Working | Uses YouTube Data API v3, searches videos matching your query, pulls top-level comments |
| **Live Reddit Comments** | ❌ Disabled | See below |

**Why Reddit is disabled:** the original integration used `api.pushshift.io`, which has had no public access since Reddit's 2023 API changes. Beyond that, Reddit's [Responsible Builder Policy](https://support.reddithelp.com/hc/en-us/articles/42728983564564-Responsible-Builder-Policy) (updated June 2026) now requires explicit approval before accessing Reddit data via API, and separately restricts using that data for LLM-based analysis without written approval. Rather than work around this or silently fail, `reddit_ingest.py` always returns an empty result with a clear, documented reason — the UI shows exactly why and falls back to the sample dataset.

---

## 🛠️ Tech Stack

- **Python** + **Streamlit** — interactive UI
- **Groq API** (`llama-3.1-8b-instant`) — LLM-based extraction and scoring
- **YouTube Data API v3** — live comment ingestion
- **pandas** — data handling
- **python-dotenv** — environment/secrets management

---

## 🚀 Running locally

### 1. Clone and set up a virtual environment
```bash
git clone https://github.com/Aaradhya1807/Noise2Signal.git
cd healthkart_flavour_scout
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Add your API keys
Create a `.env` file in the project root:
```
GROQ_API_KEY=your_groq_api_key_here
YOUTUBE_API_KEY=your_youtube_api_key_here
```
- Groq key: [console.groq.com](https://console.groq.com) → API Keys
- YouTube key: [Google Cloud Console](https://console.cloud.google.com) → enable "YouTube Data API v3" → create an API key

### 4. Run it
```bash
streamlit run app.py
```
Opens at `http://localhost:8501`.

### 5. Try it
- Pick one or more **Analysis Angles** (or define a custom one)
- Pick a **Data Source** — start with "Sample Dataset" to confirm your Groq key works without needing live data
- Click **Analyze with AI**

---

## 📁 Project structure

```
├── app.py                  # Streamlit UI + analysis pipeline (per-angle extraction, filtering, scoring)
├── domains.py               # Preset domain configs — add a new category here, no other changes needed
├── youtube_ingest.py         # Live YouTube comment ingestion (YouTube Data API v3)
├── reddit_ingest.py          # Disabled — see "Data sources" above for why
├── data/
│   └── social_chatter.csv    # Sample dataset fallback
├── requirements.txt
└── .env                      # Not committed — holds your API keys
```

---

## ⚠️ Known limitations

- **Small model, occasional misses**: `llama-3.1-8b-instant` is fast and cheap but not perfectly reliable at strict "don't invent" instructions. The grounding and vocabulary filters catch most hallucinations, but they're a safety net, not a perfect classifier.
- **Vocabulary filters are heuristic, not exhaustive**: a genuinely valid but unusual item (e.g. an uncommon flavor name) could get filtered out if it doesn't match the curated keyword list in `domains.py`. This is an intentional trade-off — a missed valid item is safer than a fabricated one showing up as a real insight.
- **Reddit ingestion is disabled** (see above) — YouTube and the sample dataset are the two working live-adjacent sources.
- **Single comment batch per run**: doesn't currently paginate/chunk very large comment volumes — fine for a demo, would need batching for production scale.

---

## 🔮 Future enhancements

- Likes-weighted trend scoring (currently unweighted by comment popularity)
- Time-based trend momentum tracking
- Confidence intervals on recommendations
- Multi-source signal blending (once a compliant Reddit-equivalent data source is available)

---

## 👤 Author

**Aaradhya Maharishi** — Data Analytics & Product Analytics Enthusiast
