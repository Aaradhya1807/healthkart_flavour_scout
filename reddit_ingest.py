import pandas as pd

# ================================================================
# Live Reddit ingestion is intentionally disabled.
#
# Why:
# 1. The old approach used api.pushshift.io, which has had no public
#    access since Reddit's 2023 API changes — that call would just
#    fail or time out.
# 2. Reddit's Responsible Builder Policy (updated June 2026) now
#    requires explicit approval before accessing Reddit data through
#    their API, and separately prohibits "mining, scraping, or using
#    data for purposes like ... to train machine learning or AI
#    models" without written approval:
#    https://support.reddithelp.com/hc/en-us/articles/42728983564564-Responsible-Builder-Policy
#
# This project feeds comments to an LLM for scoring, which sits close
# enough to that restriction that it isn't worth the compliance risk
# for a portfolio/demo project. Rather than silently failing or
# working around the policy, this module returns an empty result with
# a clear reason, and app.py falls back to the sample dataset.
#
# If you later get approved access (e.g. through the Reddit for
# Researchers Program, or written commercial approval), you can
# re-implement fetch_reddit_comments() using PRAW or the official
# Data API under those terms.
# ================================================================

DISABLED_REASON = (
    "Live Reddit ingestion is disabled: Reddit's Responsible Builder Policy "
    "(June 2026) requires explicit approval before accessing Reddit data via "
    "the API, and restricts using that data for LLM-based analysis without "
    "written approval. See README for details."
)


def fetch_reddit_comments(keyword="protein flavor", limit=100):
    """
    Live Reddit ingestion is disabled for policy-compliance reasons (see
    module docstring above). Always returns an empty DataFrame so callers
    fall back to the sample dataset cleanly.
    """
    return pd.DataFrame({"comment": []})


def get_disabled_reason() -> str:
    """Lets the UI show *why* this source returned nothing, instead of
    just silently falling back."""
    return DISABLED_REASON