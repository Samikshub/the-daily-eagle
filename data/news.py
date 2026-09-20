import re
from datetime import datetime, timezone

import feedparser
import pandas as pd
import streamlit as st
from dateutil import parser as date_parser

from data.news_sources import NEWS_SOURCES


# =========================================================
# FINANCE KEYWORDS
# =========================================================

FINANCE_KEYWORDS = [
    "stock",
    "stocks",
    "equity",
    "equities",
    "share",
    "shares",
    "s&p",
    "nasdaq",
    "dow",
    "russell",
    "futures",
    "bond",
    "bonds",
    "treasury",
    "yield",
    "yields",
    "credit",
    "spread",
    "spreads",
    "forex",
    "currency",
    "dollar",
    "federal reserve",
    "fed",
    "ecb",
    "bank of england",
    "bank of japan",
    "interest rate",
    "interest rates",
    "inflation",
    "cpi",
    "ppi",
    "pce",
    "gdp",
    "unemployment",
    "jobs",
    "payrolls",
    "tariff",
    "tariffs",
    "earnings",
    "revenue",
    "profit",
    "profits",
    "guidance",
    "acquisition",
    "acquisitions",
    "merger",
    "mergers",
    "m&a",
    "ipo",
    "buyback",
    "dividend",
    "debt",
    "bankruptcy",
    "downgrade",
    "upgrade",
    "oil",
    "crude",
    "wti",
    "brent",
    "gold",
    "silver",
    "copper",
    "natural gas",
    "bank",
    "banks",
    "financial",
    "finance",
    "private equity",
    "venture capital",
    "hedge fund",
]


# =========================================================
# NEWS CATEGORY KEYWORDS
# =========================================================

CATEGORY_KEYWORDS = {

    "Macro & Central Banks": [
        "federal reserve",
        "fed ",
        "fed's",
        "powell",
        "ecb",
        "bank of england",
        "bank of japan",
        "central bank",
        "interest rate",
        "interest rates",
        "rate cut",
        "rate hike",
        "inflation",
        "cpi",
        "ppi",
        "pce",
        "gdp",
        "unemployment",
        "payrolls",
        "jobs report",
        "tariff",
        "tariffs",
        "fiscal",
        "monetary policy",
    ],

    "Investment Banking & M&A": [
        "acquisition",
        "acquire",
        "acquires",
        "acquired",
        "merger",
        "mergers",
        "m&a",
        "takeover",
        "takeover bid",
        "buyout",
        "leveraged buyout",
        "lbo",
        "ipo",
        "initial public offering",
        "secondary offering",
        "follow-on offering",
        "equity offering",
        "debt offering",
        "bond offering",
        "capital raise",
        "capital raising",
        "private equity",
        "venture capital",
        "activist investor",
        "activist campaign",
        "shareholder activism",
        "strategic investment",
        "minority stake",
        "majority stake",
        "spin-off",
        "spinoff",
        "divestiture",
        "divestment",
        "restructuring",
        "bankruptcy",
        "chapter 11",
        "recapitalization",
        "joint venture",
        "dealmaking",
    ],

    "Technology": [
        "artificial intelligence",
        " ai ",
        "semiconductor",
        "semiconductors",
        "chip",
        "chips",
        "software",
        "cloud",
        "data center",
        "data centers",
        "cybersecurity",
        "robotics",
        "openai",
        "nvidia",
        "microsoft",
        "apple",
        "google",
        "alphabet",
        "amazon",
        "meta",
        "oracle",
    ],

    "Energy & Commodities": [
        "oil",
        "crude",
        "wti",
        "brent",
        "natural gas",
        "lng",
        "gold",
        "silver",
        "copper",
        "commodity",
        "commodities",
        "opec",
        "mining",
    ],

    "Financial Services": [
        "bank",
        "banks",
        "banking",
        "lender",
        "lending",
        "private equity",
        "hedge fund",
        "asset manager",
        "asset management",
        "wealth management",
        "insurance",
        "brokerage",
        "credit card",
    ],

    "Markets": [
        "stock",
        "stocks",
        "equity",
        "equities",
        "s&p",
        "nasdaq",
        "dow",
        "russell",
        "futures",
        "treasury",
        "bond",
        "bonds",
        "yield",
        "yields",
        "forex",
        "currency",
        "dollar",
        "market rally",
        "market selloff",
        "bull market",
        "bear market",
    ],
}


# =========================================================
# SPORTS KEYWORDS
# =========================================================

SPORTS_KEYWORDS = [
    "ufc",
    "mma",
    "nfl",
    "nba",
    "nhl",
    "mlb",
    "ncaa",
    "college football",
    "college basketball",
    "football",
    "basketball",
    "baseball",
    "hockey",
    "soccer",
    "premier league",
    "champions league",
    "world cup",
    "super bowl",
    "touchdown",
    "quarterback",
    "coach",
    "head coach",
    "athlete",
    "olympics",
    "olympic",
    "wrestling",
]


# =========================================================
# TEXT CLEANING
# =========================================================

def clean_text(text):

    if not text:
        return ""

    text = re.sub(
        r"<[^<]+?>",
        " ",
        str(text)
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def normalize_title(title):

    title = clean_text(title).lower()

    title = re.sub(
        r"[^\w\s]",
        "",
        title
    )

    title = re.sub(
        r"\s+",
        " ",
        title
    )

    return title.strip()


# =========================================================
# DATE PARSING
# =========================================================

def parse_published_date(value):

    if not value:
        return pd.NaT

    try:

        parsed = date_parser.parse(value)

        if parsed.tzinfo is None:

            parsed = parsed.replace(
                tzinfo=timezone.utc
            )

        return parsed.astimezone(
            timezone.utc
        )

    except Exception:

        return pd.NaT


# =========================================================
# RSS FEED FETCHING
# =========================================================

def fetch_feed(
    source,
    feed_category
):

    if not source.get("url"):
        return []

    try:

        feed = feedparser.parse(
            source["url"]
        )

        articles = []

        for entry in feed.entries:

            title = clean_text(
                entry.get(
                    "title",
                    ""
                )
            )

            description = clean_text(
                entry.get(
                    "summary",
                    entry.get(
                        "description",
                        ""
                    )
                )
            )

            url = entry.get(
                "link",
                ""
            )

            published_raw = entry.get(
                "published",
                entry.get(
                    "updated",
                    ""
                )
            )

            published = parse_published_date(
                published_raw
            )

            if not title or not url:
                continue

            articles.append({

                "title": title,

                "normalized_title":
                    normalize_title(
                        title
                    ),

                "description":
                    description,

                "url":
                    url,

                "published":
                    published,

                "published_raw":
                    published_raw,

                "source":
                    source["name"],

                "source_priority":
                    source.get(
                        "priority",
                        1
                    ),

                "feed_category":
                    feed_category,
            })

        return articles

    except Exception:

        return []


# =========================================================
# FINANCE RELEVANCE SCORE
# =========================================================

def calculate_finance_score(
    title,
    description,
    feed_category
):

    text = (
        f" {title} {description} "
    ).lower()

    score = 0

    for keyword in FINANCE_KEYWORDS:

        if keyword in text:
            score += 1

    # Finance-specific feeds get
    # a small relevance boost.

    if feed_category in [
        "markets",
        "business",
        "macro",
        "commodities",
    ]:

        score += 1

    return score


# =========================================================
# CATEGORY SCORING
# =========================================================

def calculate_category_scores(
    title,
    description
):

    text = (
        f" {title} {description} "
    ).lower()

    scores = {}

    for (
        category,
        keywords
    ) in CATEGORY_KEYWORDS.items():

        score = 0

        for keyword in keywords:

            if keyword in text:
                score += 1

        scores[category] = score

    return scores


# =========================================================
# ARTICLE CLASSIFICATION
# =========================================================

def classify_article(
    title,
    description,
    feed_category
):

    title_text = clean_text(title).lower()
    description_text = clean_text(description).lower()

    text = (
        f" {title_text} {description_text} "
    )

    # -----------------------------------------------------
    # SPORTS FILTER
    # -----------------------------------------------------

    if any(
        keyword in text
        for keyword in SPORTS_KEYWORDS
    ):
        return "Miscellaneous"

    # -----------------------------------------------------
    # INVESTMENT BANKING / M&A
    # -----------------------------------------------------
    #
    # We intentionally require the headline to contain
    # explicit transaction / capital-markets language.
    # This keeps unrelated stories out of the IB section.
    #

    ib_headline_keywords = [

        # M&A
        "acquisition",
        "acquires",
        "acquire",
        "acquired",
        "merger",
        "mergers",
        "m&a",
        "takeover",
        "takeover bid",
        "buyout",
        "leveraged buyout",
        "lbo",

        # Equity / capital markets
        "ipo",
        "initial public offering",
        "secondary offering",
        "follow-on offering",
        "follow on offering",
        "equity offering",
        "debt offering",
        "bond offering",
        "capital raise",
        "capital raising",

        # Private capital
        "private equity",
        "venture capital",

        # Activism / ownership
        "activist investor",
        "activist campaign",
        "shareholder activism",
        "strategic investment",
        "minority stake",
        "majority stake",

        # Corporate actions
        "spin-off",
        "spinoff",
        "divestiture",
        "divestment",
        "recapitalization",
        "joint venture",

        # Restructuring
        "restructuring",
        "bankruptcy",
        "chapter 11",
    ]

    if any(
        keyword in title_text
        for keyword in ib_headline_keywords
    ):

        return "Investment Banking & M&A"

    # -----------------------------------------------------
    # OTHER CATEGORIES
    # -----------------------------------------------------

    scores = calculate_category_scores(
        title,
        description
    )

    best_category = max(
        scores,
        key=scores.get
    )

    best_score = scores[
        best_category
    ]

    if best_score > 0:

        return best_category

    # -----------------------------------------------------
    # FALLBACK
    # -----------------------------------------------------

    fallback_categories = {

        "markets":
            "Markets",

        "business":
            "Miscellaneous",

        "technology":
            "Technology",

        "macro":
            "Macro & Central Banks",

        "commodities":
            "Energy & Commodities",

        "misc":
            "Miscellaneous",
    }

    return fallback_categories.get(
        feed_category,
        "Miscellaneous"
    )


# =========================================================
# RECENCY SCORE
# =========================================================

def calculate_recency_score(
    published
):

    if pd.isna(published):

        return 0

    now = datetime.now(
        timezone.utc
    )

    age_hours = (
        now - published
    ).total_seconds() / 3600

    if age_hours <= 6:
        return 5

    if age_hours <= 12:
        return 4

    if age_hours <= 24:
        return 3

    if age_hours <= 48:
        return 2

    if age_hours <= 72:
        return 1

    return 0


# =========================================================
# OVERALL RANKING SCORE
# =========================================================

def calculate_rank_score(
    row
):

    finance_score = (
        row["finance_score"] * 2
    )

    source_score = (
        row["source_priority"] * 2
    )

    recency_score = (
        row["recency_score"] * 3
    )

    return (
        finance_score
        + source_score
        + recency_score
    )


# =========================================================
# MAIN NEWS FUNCTION
# =========================================================

@st.cache_data(ttl=600)
def get_news():

    all_articles = []

    # -----------------------------------------------------
    # FETCH ALL RSS SOURCES
    # -----------------------------------------------------

    for (
        feed_category,
        sources
    ) in NEWS_SOURCES.items():

        for source in sources:

            articles = fetch_feed(
                source,
                feed_category
            )

            all_articles.extend(
                articles
            )

    if not all_articles:

        return pd.DataFrame()

    # -----------------------------------------------------
    # CREATE DATAFRAME
    # -----------------------------------------------------

    df = pd.DataFrame(
        all_articles
    )

    # -----------------------------------------------------
    # REMOVE BLANK TITLES
    # -----------------------------------------------------

    df = df[
        df["title"].notna()
    ]

    df = df[
        df["title"].str.strip()
        != ""
    ]

    # -----------------------------------------------------
    # REMOVE DUPLICATE HEADLINES
    # -----------------------------------------------------

    df = df.drop_duplicates(
        subset=[
            "normalized_title"
        ],
        keep="first"
    )

    # -----------------------------------------------------
    # FINANCIAL RELEVANCE
    # -----------------------------------------------------

    df["finance_score"] = (
        df.apply(
            lambda row:
                calculate_finance_score(
                    row["title"],
                    row["description"],
                    row["feed_category"]
                ),
            axis=1
        )
    )

    # -----------------------------------------------------
    # ARTICLE CATEGORY
    # -----------------------------------------------------

    df["category"] = (
        df.apply(
            lambda row:
                classify_article(
                    row["title"],
                    row["description"],
                    row["feed_category"]
                ),
            axis=1
        )
    )

    # -----------------------------------------------------
    # RECENCY
    # -----------------------------------------------------

    df["recency_score"] = (
        df["published"].apply(
            calculate_recency_score
        )
    )

    # -----------------------------------------------------
    # OVERALL RANKING
    # -----------------------------------------------------

    df["rank_score"] = (
        df.apply(
            calculate_rank_score,
            axis=1
        )
    )

    # -----------------------------------------------------
    # FINANCE FLAG
    # -----------------------------------------------------

    df["is_finance"] = (
        df["finance_score"] >= 1
    )

    # -----------------------------------------------------
    # SORT ARTICLES
    # -----------------------------------------------------

    df = df.sort_values(
        by=[
            "rank_score",
            "published"
        ],
        ascending=[
            False,
            False
        ],
        na_position="last"
    )

    return df.reset_index(
        drop=True
    )