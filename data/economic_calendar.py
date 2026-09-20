import requests
import pandas as pd
import streamlit as st

from datetime import datetime, timedelta


BASE_URL = "https://www.financecalendar.com/wp-json/fc/v1"


# =========================================================
# MARKET RELEVANCE KEYWORDS
# =========================================================

HIGH_PRIORITY_KEYWORDS = [

    # -----------------------------------------------------
    # US FED / MONETARY POLICY
    # -----------------------------------------------------

    "federal reserve",
    "fed",
    "fomc",
    "fed interest rate",
    "fed funds",
    "interest rate decision",
    "rate decision",
    "central bank",

    # -----------------------------------------------------
    # INFLATION
    # -----------------------------------------------------

    "consumer price index",
    "cpi",
    "core cpi",
    "personal consumption expenditures",
    "pce",
    "core pce",
    "producer price index",
    "ppi",
    "inflation",

    # -----------------------------------------------------
    # EMPLOYMENT
    # -----------------------------------------------------

    "nonfarm payrolls",
    "non-farm payrolls",
    "payrolls",
    "employment report",
    "unemployment rate",
    "unemployment",
    "initial jobless claims",
    "jobless claims",
    "adp employment",
    "jobs report",

    # -----------------------------------------------------
    # GROWTH
    # -----------------------------------------------------

    "gross domestic product",
    "gdp",
    "retail sales",
    "industrial production",
    "durable goods",
    "housing starts",
    "building permits",

    # -----------------------------------------------------
    # BUSINESS ACTIVITY
    # -----------------------------------------------------

    "ism manufacturing",
    "ism services",
    "ism non-manufacturing",
    "pmi",
    "manufacturing pmi",
    "services pmi",

    # -----------------------------------------------------
    # CONSUMER
    # -----------------------------------------------------

    "consumer confidence",
    "consumer sentiment",
    "michigan sentiment",

    # -----------------------------------------------------
    # CENTRAL BANKS
    # -----------------------------------------------------

    "ecb",
    "bank of england",
    "boe",
    "bank of japan",
    "boj",
    "people's bank of china",
    "pboc",
]


MEDIUM_PRIORITY_KEYWORDS = [

    "trade balance",
    "exports",
    "imports",
    "current account",
    "business confidence",
    "economic confidence",
    "industrial production",
    "factory orders",
    "wholesale inventories",
    "business inventories",
    "new home sales",
    "existing home sales",
    "pending home sales",
    "construction spending",
    "capacity utilization",
    "leading indicators",
    "consumer credit",
    "mortgage applications",
    "crude oil inventories",
]


LOW_PRIORITY_KEYWORDS = [

    "holiday",
    "market holiday",
    "bank holiday",
    "stock market holiday",
    "public holiday",
    "national holiday",
    "respect for the aged day",
    "market closed",
    "market open",
    "trading hours",
    "trading holiday",
    "exchange holiday",
    "exchange hours",
]

EXCLUDED_EVENT_KEYWORDS = [

    "holiday",
    "market holiday",
    "bank holiday",
    "stock market holiday",
    "public holiday",
    "national holiday",
    "respect for the aged day",
    "market closed",
    "market open",
    "trading hours",
    "trading holiday",
    "exchange holiday",
    "exchange hours",
]


# =========================================================
# EVENT RELEVANCE SCORE
# =========================================================

def calculate_event_relevance(row):

    text = " ".join(
        [
            str(row.get("event", "")),
            str(row.get("title", "")),
            str(row.get("category", "")),
        ]
    ).lower()

    score = 0

    # -----------------------------------------------------
    # Impact
    # -----------------------------------------------------

    impact = str(
        row.get("impact", "")
    ).lower()

    if impact == "high":
        score += 8

    elif impact == "medium":
        score += 3

    elif impact == "low":
        score += 0


    # -----------------------------------------------------
    # High-priority keywords
    # -----------------------------------------------------

    for keyword in HIGH_PRIORITY_KEYWORDS:

        if keyword in text:

            score += 5

            break


    # -----------------------------------------------------
    # Medium-priority keywords
    # -----------------------------------------------------

    for keyword in MEDIUM_PRIORITY_KEYWORDS:

        if keyword in text:

            score += 2

            break


    # -----------------------------------------------------
    # Low-value events
    # -----------------------------------------------------

    for keyword in LOW_PRIORITY_KEYWORDS:

        if keyword in text:

            score -= 10

            break


    # -----------------------------------------------------
    # US / major developed-market preference
    # -----------------------------------------------------

    country_text = text

    if any(
        country in country_text
        for country in [
            "united states",
            "us ",
            "u.s.",
            "america",
            "federal reserve",
            "fed",
        ]
    ):

        score += 2


    return score


# =========================================================
# ECONOMIC CALENDAR
# =========================================================

@st.cache_data(ttl=300)
def get_economic_calendar():

    today = datetime.now().date()

    next_week = (
        today
        + timedelta(days=7)
    )


    params = {

        "from":
            today.strftime(
                "%Y-%m-%d"
            ),

        "to":
            next_week.strftime(
                "%Y-%m-%d"
            ),

        "limit":
            500
    }


    try:

        response = requests.get(
            f"{BASE_URL}/calendar",
            params=params,
            timeout=15
        )

        response.raise_for_status()

        data = response.json()


        events = data.get(
            "events",
            []
        )


        if not events:

            return pd.DataFrame()


        df = pd.DataFrame(
            events
        )


        # -------------------------------------------------
        # RENAME FIELDS
        # -------------------------------------------------

        df = df.rename(
            columns={
                "name":
                    "event",

                "prior":
                    "previous"
            }
        )


        # -------------------------------------------------
        # SOURCE
        # -------------------------------------------------

        df["source"] = (
            "FinanceCalendar.com"
        )


        df["source_url"] = df.get(
            "url",
            "https://www.financecalendar.com/"
        )


        # -------------------------------------------------
        # EXPECTED COLUMNS
        # -------------------------------------------------

        expected_columns = [

            "date",
            "time_et",
            "event",
            "title",
            "impact",
            "category",
            "consensus",
            "previous",
            "actual",
            "source",
            "source_url"
        ]


        for column in expected_columns:

            if column not in df.columns:

                df[column] = None


        df = df[
            expected_columns
        ]


        # -------------------------------------------------
        # CLEAN TEXT
        # -------------------------------------------------

        for column in [
            "event",
            "title",
            "impact",
            "category",
        ]:

            df[column] = (
                df[column]
                .fillna("")
                .astype(str)
            )


        # -------------------------------------------------
        # RELEVANCE SCORE
        # -------------------------------------------------

        df["relevance_score"] = (
            df.apply(
                calculate_event_relevance,
                axis=1
            )
        )
        

        # -------------------------------------------------
        # REMOVE NON-ECONOMIC CALENDAR ITEMS
        # -------------------------------------------------

        def is_excluded_event(row):

            text = " ".join(
                [
                    str(row.get("event", "")),
                    str(row.get("title", "")),
                    str(row.get("category", "")),
                ]
            ).lower()

            return any(
                keyword in text
                for keyword in EXCLUDED_EVENT_KEYWORDS
            )


        df = df[
            ~df.apply(
                is_excluded_event,
                axis=1
            )
        ]

        # -------------------------------------------------
        # REMOVE CLEARLY IRRELEVANT EVENTS
        # -------------------------------------------------

        df = df[
            df["relevance_score"] >= 3
        ]


        # -------------------------------------------------
        # SORT
        # -------------------------------------------------

        df = df.sort_values(
            by=[
                "relevance_score",
                "date",
                "time_et",
            ],
            ascending=[
                False,
                True,
                True,
            ],
            na_position="last"
        )


        return df.reset_index(
            drop=True
        )


    except Exception as e:

        st.error(
            f"Unable to load economic calendar: {e}"
        )

        return pd.DataFrame()