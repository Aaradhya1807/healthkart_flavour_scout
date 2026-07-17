"""
Preset domain configurations for the Signal Scout Engine.

Each preset tells the engine:
- what kind of "item" it's extracting (a flavor, a phone feature, a colorway...)
- how to describe that domain to the LLM
- a lightweight keyword gate to skip obviously irrelevant comment batches
  before spending an API call (context_keywords)
- brand/company/product names to strip out, so the LLM doesn't return
  "Samsung" as a "feature" or "Saucony Trainer 80" as a "colorway"
  (brand_keywords)
- an optional positive vocabulary check: if the real answer in this domain
  almost always contains a predictable word (a colorway almost always
  contains a color name; a spec almost always contains a tech word), list
  those words here. Any extracted item containing NONE of them gets
  discarded — this catches brand/model names slipping through as a
  category mismatch, which an ever-growing brand denylist can't fully
  cover (item_must_contain_one_of). Leave empty ([]) to skip this check
  for domains where the item itself IS a name/brand (e.g. phone models).

Add a new preset by copying one of these dicts — nothing else in app.py
needs to change.
"""

PRESETS = {
    "HealthKart Flavors": {
        "item_label": "flavor",
        "domain_description": "flavors of nutrition, supplement, or protein products",
        "valid_examples": "vanilla, chocolate, mango mint, cookie blast",
        "invalid_examples": "brands, companies, tech terms, abstract concepts",
        "context_keywords": [
            "flavour", "flavor", "taste", "tasty", "sweet", "sour",
            "vanilla", "chocolate", "strawberry", "mango", "mint",
            "cookie", "banana", "whey", "protein", "shake", "ice cream", "drink",
        ],
        "brand_keywords": [
            "ryse", "ghost", "optimum", "dymatize", "labrada",
            "ascent", "myprotein", "healthkart",
        ],
        "item_must_contain_one_of": [
            "vanilla", "chocolate", "strawberry", "mango", "mint", "cookie",
            "banana", "coffee", "caramel", "hazelnut", "peanut", "butter",
            "berry", "coconut", "pineapple", "orange", "lemon", "lime",
            "watermelon", "guava", "litchi", "rose", "cardamom", "elaichi",
            "kesar", "saffron", "pista", "pistachio", "almond", "honey",
            "malai", "kulfi", "gulab jamun", "cream", "fudge", "brownie",
        ],
        "default_query": "whey protein flavours",
        "brand_fit_label": "Brand Fit (nutrition brand)",
    },
    "Phone Models (Comparison)": {
        "item_label": "phone model",
        "domain_description": (
            "specific phone models or variants that people recommend, compare, "
            "ask about, or complain about in the comments"
        ),
        "valid_examples": "a specific model name people actually typed, like a brand + model + variant combination",
        "invalid_examples": (
            "specs/features on their own (e.g. 'camera', 'battery'), prices, generic "
            "terms like 'phone' or 'smartphone', non-phone accessories (e.g. AirPods, earbuds)"
        ),
        "context_keywords": [],  # too many valid phone names to enumerate — skip the gate, rely on grounding filter
        "brand_keywords": [
            "airpods", "galaxy buds", "earbuds", "smartwatch",
        ],
        "item_must_contain_one_of": [],  # the item IS a name/model here — no vocabulary restriction
        "default_query": "best smartphone recommendations 2026",
        "brand_fit_label": "Recommendation Strength (strongly recommended, not just mentioned)",
    },
    "Phone Specs & Features": {
        "item_label": "spec or feature",
        "domain_description": "smartphone specs or features people want, praise, or complain about",
        "valid_examples": "108MP camera, fast charging, AMOLED display, in-display fingerprint, 120Hz refresh rate",
        "invalid_examples": "brand names, model numbers, prices, generic praise like 'great phone'",
        "context_keywords": [
            "camera", "battery", "display", "screen", "charging", "chipset",
            "processor", "ram", "storage", "refresh rate", "fingerprint",
            "zoom", "design", "build quality",
        ],
        "brand_keywords": [
            "samsung", "apple", "iphone", "oneplus", "xiaomi", "redmi",
            "oppo", "vivo", "realme", "google", "pixel", "nothing phone",
            "airpods", "galaxy buds", "earbuds", "moto edge", "motorola",
        ],
        "item_must_contain_one_of": [
            "camera", "battery", "display", "screen", "charging", "chipset",
            "processor", "ram", "storage", "refresh", "fingerprint", "zoom",
            "design", "build", "resolution", "megapixel", "mp", "stabiliz",
            "waterproof", "ip68", "wireless", "gaming", "speaker", "audio",
            "stylus", "notch", "bezel", "curved", "sensor",
        ],
        "default_query": "best smartphone features 2026",
        "brand_fit_label": "Brand Fit (flagship-tier feature)",
    },
    "Sneaker Colorways": {
        "item_label": "colorway",
        "domain_description": "sneaker colorways or designs people are excited about or want restocked",
        "valid_examples": "triple black, chicago colorway, panda, university blue, bred",
        "invalid_examples": "brand names, model names, prices, sizing complaints",
        "context_keywords": [
            "colorway", "colour", "color", "edition", "drop",
            "release", "restock", "sneaker", "shoe", "pair",
        ],
        "brand_keywords": [
            "nike", "adidas", "puma", "reebok", "new balance", "asics",
            "jordan", "yeezy", "onitsuka", "saucony", "converse", "vans", "samba",
        ],
        "item_must_contain_one_of": [
            "black", "white", "blue", "red", "green", "yellow", "pink",
            "grey", "gray", "purple", "orange", "brown", "beige", "gold",
            "silver", "navy", "maroon", "teal", "olive", "panda", "chicago",
            "bred", "royal", "triple", "university", "multi", "camo",
            "tie-dye", "gradient", "colorway", "colourway", "edition",
        ],
        "default_query": "sneaker colorway drop reactions",
        "brand_fit_label": "Brand Fit (sneaker culture appeal)",
    },
}


def custom_domain(item_label: str, domain_description: str,
                   brand_keywords_csv: str = "", context_keywords_csv: str = "") -> dict:
    """Build a domain config from free-text user input (the 'Custom' option)."""
    brand_keywords = [b.strip().lower() for b in brand_keywords_csv.split(",") if b.strip()]
    context_keywords = [k.strip().lower() for k in context_keywords_csv.split(",") if k.strip()]
    return {
        "item_label": item_label.strip() or "item",
        "domain_description": domain_description.strip() or "product attributes people discuss",
        "valid_examples": "concrete, specific mentions relevant to this category",
        "invalid_examples": "brand names, company names, prices, vague praise",
        "context_keywords": context_keywords,  # empty list = skip the relevance gate
        "brand_keywords": brand_keywords,
        # Custom domains reuse the same keyword list as a soft per-item
        # vocabulary check (better than nothing; user can leave it blank
        # to skip this check entirely).
        "item_must_contain_one_of": context_keywords,
        "default_query": item_label.strip() or "product",
        "brand_fit_label": "Brand Fit",
    }