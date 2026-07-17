# 🔍 Signal Scout Engine

**AI-powered, multi-domain product signal discovery from social chatter**

Signal Scout Engine turns noisy social media comments (YouTube, Reddit) into structured, auditable ACCEPT/REJECT decisions about what people actually want — a flavor, a phone model, a spec, a sneaker colorway, or any custom category you define on the fly. Every decision is backed by a transparent, weighted scoring trace, not a black-box output.

This started as a single-purpose flavor-trend tool for HealthKart and has since been generalized into a domain-agnostic engine: the same extraction → scoring → filtering → decision pipeline now works across four built-in presets plus any custom angle a user defines, with no code changes required to add a new use case.

## 🚀 Live Demo & Code

- **Live App:** https://healthkart-flavour-scout.onrender.com
- **GitHub Repo:** https://github.com/Aaradhya1807/healthkart_flavour_scout

## 🎯 What problem this solves

Product and content decisions (which flavor to launch, which phone to recommend, which colorway to restock) often rely on intuition or lagging sales data. Social platforms carry early signals of demand, but:

- The data is noisy, unstructured, and full of sarcasm, brand chatter, and off-topic mentions
- APIs are unstable or restricted (rate limits, policy changes, quota caps)
- Raw LLM output is hard to trust or defend to a stakeholder unless every score is explainable

Signal Scout addresses this with a resilient ingestion layer, an LLM scoring engine that stays grounded in the actual comments, and a three-layer filter that catches hallucinations and category mismatches before they reach the decision stage.

## 🧠 How it works

### 1. Pick one or more analysis angles
Choose from four presets — **HealthKart Flavors**, **Phone Models (Comparison)**, **Phone Specs & Features**, **Sneaker Colorways** — or open **➕ Add a custom angle** to define any category on the spot (item type, one-line domain description, brands to exclude, optional relevance keywords). Multiple angles can run against the same comment batch in a single pass, and each is scored completely independently — a phone model is never ranked against a camera spec.

### 2. Ingest comments
- **YouTube (live):** searches for videos matching the angle's query and pulls top-level comments via the official YouTube Data API v3. Results are cached (`@st.cache_data`, 10-minute TTL) so repeated runs with the same query don't re-hit the API.
- **Reddit (currently disabled by design):** see [Reddit ingestion](#-reddit-ingestion--intentionally-disabled) below.
- **Sample dataset (fallback):** used automatically whenever a live source returns nothing — missing API key, exhausted quota, no matching videos, or a disabled live source — so the app always has something to show.

### 3. Extract and score, per angle
For each selected angle, comments are sent to Groq (`llama-3.1-8b-instant`) with a strict prompt: extract only items that are actually grounded in the text, and score each one on four independent 0–100 components:

| Component | Weight | What it captures |
|---|---|---|
| Trend Strength | 35% | How frequently and prominently the item is mentioned |
| Sentiment Strength | 30% | How positively people react to it |
| Brand Fit | 20% | Angle-specific — e.g. recommendation strength, flagship-tier fit, sneaker-culture appeal |
| Signal Quality | 15% | How clear vs. vague/sarcastic the mentions are |

The model returns only the four raw components — **it never computes the final score itself.** `final_score` is calculated in code as a genuine weighted average of those components, so a result can't drift from what the comments actually support, and doesn't depend on how many other items happen to be in the same batch.

### 4. Three-layer filtering
Before anything reaches the decision stage, every extracted item has to survive:

1. **Brand denylist** — strips obvious brand/company names out of the item field (e.g. so "Samsung" can't show up as a phone "feature").
2. **Grounding check** — the item (or its significant words) must actually appear in the source comments. Anything that doesn't is discarded and surfaced in the UI as a likely hallucination, regardless of how well the model followed instructions.
3. **Positive vocabulary check** (`item_must_contain_one_of`) — for domains where a valid answer has a predictable vocabulary (a colorway almost always contains a color word; a spec almost always contains a tech term), the item must contain at least one of those words. This is what catches brand/model names slipping through as a fake colorway or fake spec (e.g. "Onitsuka Tiger" or "Saucony Trainer 80" being returned as a "colorway") — a category mismatch a brand denylist alone can never fully cover, since it's impossible to enumerate every brand. Domains where the item *is* itself a name (like phone models) leave this list empty and skip the check.

Both discarded groups (ungrounded items, off-topic items) are shown in the UI with a reason, not silently dropped.

### 5. Decision rules
- `final_score ≥ 75` → **ACCEPT**
- `final_score < 75` → **REJECT**
- The highest-scoring accepted item per angle is surfaced as the **Golden Candidate**

Every row in the decision trace shows all four component scores, the final weighted score, the decision, and a plain-language reason — fully auditable, not a black box.

## 📥 Data sources

### ✅ YouTube (live)
Uses the official YouTube Data API v3 to search for videos matching the angle's query and pull top-level comments. Fails gracefully (returns nothing, not an exception) on a missing key, exhausted quota, or no matching videos — the app falls back to sample data and tells you why.

### 🚫 Reddit ingestion — intentionally disabled
Live Reddit ingestion is turned off on purpose, not because it's broken. Two reasons:

1. The old approach relied on `api.pushshift.io`, which has had no public access since Reddit's 2023 API changes.
2. Reddit's **Responsible Builder Policy** (updated June 2026) requires explicit approval before accessing Reddit data via the API, and separately restricts using that data to train or run ML/AI models without written approval. Feeding comments to an LLM for scoring sits close enough to that restriction that it isn't worth the compliance risk for a demo project.

Selecting the Reddit option in the UI shows this reason directly and falls back to sample data — it's a documented, deliberate constraint, not a silent failure. Re-enabling it would mean implementing `fetch_reddit_comments()` with PRAW or the official Data API under an approved-access agreement (e.g. the Reddit for Researchers Program).

### 🛟 Sample dataset (fallback)
Loaded automatically whenever a live source returns nothing, so a demo or analysis run is never blocked by an API outage, quota limit, or policy restriction.

## 🛠️ Tech stack

- **Streamlit** — UI
- **Groq API** (`llama-3.1-8b-instant`) — extraction + component scoring
- **YouTube Data API v3** — live comment ingestion
- **Pandas** — data handling and scoring math
- **python-dotenv** — environment/config management

## 📁 Project structure

```
app.py               # Streamlit UI, pipeline orchestration, scoring, filtering
domains.py           # Preset domain configs + custom-angle builder
youtube_ingest.py     # Live YouTube search + comment fetch
reddit_ingest.py      # Disabled by policy — returns empty + a documented reason
requirements.txt
data/social_chatter.csv   # Sample fallback dataset
```

### Adding a new preset domain
Every preset in `domains.py` is a plain dict — copying an existing one and adjusting the fields is enough to add a new category (e.g. "Cricket Players", "Restaurant Menu Items") with **no changes needed in `app.py`**. Fields to set:

- `item_label` — singular noun for what's being extracted
- `domain_description` — one line describing the category to the LLM
- `valid_examples` / `invalid_examples` — a few illustrative (not exhaustive) examples
- `context_keywords` — optional lightweight gate to skip an obviously irrelevant comment batch before spending an API call
- `brand_keywords` — names to strip out so they can't masquerade as the item
- `item_must_contain_one_of` — optional positive vocabulary check (leave `[]` for domains where the item itself is a name/brand, like phone models)
- `default_query` — default search string for live YouTube ingestion
- `brand_fit_label` — how the "Brand Fit" score should be interpreted for this domain

For anything not worth a permanent preset, the **➕ Add a custom angle** expander in the app builds the same config shape from free-text input at run time via `custom_domain()`.

## 🔐 Setup

1. Clone the repo and install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Create a `.env` file in the project root:
   ```
   GROQ_API_KEY=your_groq_key_here
   YOUTUBE_API_KEY=your_youtube_key_here
   ```
   Both are optional individually — without `GROQ_API_KEY` the analysis step is disabled with a clear error; without `YOUTUBE_API_KEY` live YouTube ingestion silently falls back to sample data.
3. Run the app:
   ```bash
   streamlit run app.py
   ```

No credentials are committed to the repo; all keys are read from environment variables via `python-dotenv`.

## 📌 Key design decisions

- **Weighted scoring, not rank-based placeholders.** An earlier version replaced the LLM's actual component scores with a synthetic linear scale based only on rank position. The current version keeps the four real component scores and computes `final_score` as a genuine weighted average, so a result reflects the actual evidence rather than where it happened to land in a list.
- **Explainability over black-box output.** Every accepted or rejected item shows its full component breakdown and a plain-language reason — built for a demo where the reasoning needs to hold up to scrutiny, not just the headline recommendation.
- **Multiple filtering layers instead of one.** Brand denylist, grounding check, and positive vocabulary check each catch a different failure mode (obvious brand leakage, outright hallucination, and category mismatch respectively). None of them alone is sufficient — a denylist can't enumerate every brand, and a grounding check alone can't tell a real colorway from a real shoe-model name that's also present in the text.
- **Domain-agnostic by design.** Presets are configuration, not code — the same pipeline generalizes to any category with a config change, and the custom-angle form covers everything else without waiting on a code deploy.
- **Compliance treated as a real constraint.** Reddit ingestion is disabled on purpose given current platform policy, and that reasoning is documented in code and surfaced in the UI rather than worked around.
- **Graceful degradation everywhere.** Missing keys, exhausted quotas, empty search results, and disabled sources all fall back to sample data with a visible explanation instead of crashing or failing silently.

## 🚀 Future enhancements

- Chunking + aggregation for large comment volumes (current single-prompt approach can hit token limits at scale)
- Unit tests for the grounding/vocabulary filters and the scoring function
- Likes-weighted trend scoring
- Splitting `app.py` into smaller modules (scoring, filtering, prompts) as more presets are added

## 🧠 Final note

Signal Scout Engine is a decision-support tool, not a prediction system — it's built to make its reasoning fully inspectable, so a human can trust (or challenge) exactly why an item was accepted or rejected.

## 👤 Author

**Aaradhya Maharishi**
Data Analytics & Product Analytics Enthusiast
