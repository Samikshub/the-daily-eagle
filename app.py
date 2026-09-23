import streamlit as st
import pandas as pd

from datetime import datetime, time
from zoneinfo import ZoneInfo

from config.assets import INDICES, SP100
from data.markets import get_market_data
from data.treasuries import get_treasury_data
from data.commodities import get_commodity_data
from data.economic_calendar import get_economic_calendar
from data.news import get_news
from data.ticker import get_sp100_ticker_data
from components.charts import create_yield_curve

# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="The Daily Eagle",
    page_icon="🦅",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# =========================================================
# GLOBAL DESIGN SYSTEM
# =========================================================

st.markdown(
    """
    
<style>

.tde-footer {
    margin-top: 4rem;
    padding-bottom: 2rem;
    text-align: center;
    font-family: Georgia, "Times New Roman", serif;
    font-size: 0.75rem;
    font-style: italic;
    color: var(--cream-muted);
    letter-spacing: 0.03em;
}

:root {
    --navy: #0F1826;
    --navy-light: #162235;
    --cream: #EDE6D6;
    --cream-muted: #B9C2D4;
    --gold: #C9A14B;
    --gold-light: #D8B96A;
    --border: #354052;
}


/* =====================================================
   GLOBAL PAGE
   ===================================================== */

.stApp {
    background-color: var(--navy);
    color: var(--cream);
}

.main {
    background-color: var(--navy);
}

html,
body,
[class*="css"] {
    font-family:
        Inter,
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        sans-serif;

    color: var(--cream);
}

/* =====================================================
   HEADER MARKET STATUS
   ===================================================== */

.tde-header-row {
    display: flex;

    justify-content: space-between;

    align-items: flex-end;

    gap: 2rem;
}

.tde-market-status {
    text-align: right;

    padding-bottom: 0.15rem;
}

.tde-date {
    font-family:
        Georgia,
        "Times New Roman",
        serif;

    color:
        var(--cream);

    font-size: 1rem;

    margin-bottom: 0.35rem;
}

.market-open,
.market-closed {
    font-family:
        Inter,
        sans-serif;

    font-size: 0.75rem;

    font-weight: 700;

    letter-spacing: 0.1em;
}

.market-open {
    color:
        #7FBF8F;
}

.market-closed {
    color:
        var(--gold);
}

.tde-market-description {
    font-family:
        Inter,
        sans-serif;

    color:
        var(--cream-muted);

    font-size: 0.68rem;

    margin-top: 0.25rem;
}


/* =====================================================
   S&P 100 TICKER
   ===================================================== */

.ticker-wrapper {
    width: 100vw !important;
    max-width: none !important;

    position: relative;
    left: 50%;

    transform: translateX(-50%);

    overflow: hidden;

    white-space: nowrap;

    border-top:
        1px solid var(--border);

    border-bottom:
        1px solid var(--border);

    background-color:
        var(--navy-light);

    margin-bottom: 2rem;

    padding:
        0.7rem 0;

    box-sizing: border-box;
}

.ticker-track {
    display: flex;

    width: max-content;

    animation:
        ticker-scroll 180s linear infinite;
}

.ticker-wrapper:hover .ticker-track {
    animation-play-state: paused;
}

.ticker-content {
    display: flex;

    align-items: center;

    flex-shrink: 0;

}

.ticker-item {
    display: inline-block;

    margin-right: 2rem;

    font-family:
        Inter,
        sans-serif;

    font-size: 0.75rem;

    color:
        var(--cream-muted);
}

.ticker-item strong {
    color:
        var(--cream);

    font-weight: 700;

    margin-right: 0.25rem;
}

.ticker-change {
    margin-left: 0.2rem;
    font-weight: 600;
}

.ticker-change.up {
    color: #35D07F;
}

.ticker-change.down {
    color: #FF5C5C;
}

.ticker-change.flat {
    color: var(--cream-muted);
}

@keyframes ticker-scroll {

    from {
        transform:
            translateX(0);
    }

    to {
        transform:
            translateX(-50%);
    }
}

# =========================================================
# US MARKET STATUS
# =========================================================

def get_us_market_status():

    eastern = ZoneInfo("America/New_York")

    now = datetime.now(eastern)

    current_time = now.time()

    market_open = time(
        9,
        30
    )

    market_close = time(
        16,
        0
    )

    premarket_start = time(
        4,
        0
    )

    afterhours_end = time(
        20,
        0
    )


    # Weekend

    if now.weekday() >= 5:

        return (
            "CLOSED",
            now,
            "Markets closed"
        )


    # Regular session

    if (
        market_open
        <= current_time
        < market_close
    ):

        return (
            "OPEN",
            now,
            "Regular session"
        )


    # Pre-market

    if (
        premarket_start
        <= current_time
        < market_open
    ):

        return (
            "PRE-MARKET",
            now,
            "Pre-market trading"
        )


    # After-hours

    if (
        market_close
        <= current_time
        < afterhours_end
    ):

        return (
            "AFTER HOURS",
            now,
            "After-hours trading"
        )


    return (
        "CLOSED",
        now,
        "Markets closed"
    )

/* =====================================================
   HEADINGS
   ===================================================== */

h1,
h2,
h3,
h4 {
    font-family:
        Georgia,
        "Times New Roman",
        serif;

    color: var(--cream);

    letter-spacing: -0.02em;
}

h1 {
    font-size: 3.7rem !important;
    line-height: 1.05 !important;
}

h2 {
    font-size: 2rem !important;
}

h3 {
    font-size: 1.35rem !important;
}


/* =====================================================
   TDE HEADER
   ===================================================== */

.tde-header {
    padding-top: 2.5rem;
    padding-bottom: 1.5rem;

    border-bottom:
        1px solid var(--border);

    margin-bottom: 2rem;
}

.tde-title {
    font-family:
        Georgia,
        "Times New Roman",
        serif;

    font-size: 4rem;
    font-weight: 700;

    line-height: 1;

    color: var(--cream);

    letter-spacing: -0.04em;
}

.tde-title span {
    color: var(--gold);
    font-style: italic;
}

.tde-subtitle {
    font-family:
        Georgia,
        "Times New Roman",
        serif;

    font-size: 1.15rem;
    font-style: italic;

    color: var(--cream-muted);

    margin-top: 1.1rem;
}


/* =====================================================
   SECTION HEADERS
   ===================================================== */

.section-header {
    display: flex;
    align-items: center;

    gap: 1rem;

    margin-top: 2.5rem;
    margin-bottom: 1rem;

    padding-bottom: 0.55rem;

    border-bottom:
        1px solid var(--border);
}

.section-header-title {
    font-family:
        Georgia,
        "Times New Roman",
        serif;

    font-size: 1.7rem;
    font-weight: 700;

    color: var(--cream);

    letter-spacing: -0.02em;
}

.section-header-accent {
    color: var(--gold);

    font-size: 0.8rem;
    font-weight: 700;

    text-transform: uppercase;

    letter-spacing: 0.12em;
}


/* =====================================================
   REGIONAL HEADERS
   ===================================================== */

.region-title {
    font-family:
        Georgia,
        "Times New Roman",
        serif;

    color: var(--cream);

    font-size: 1.2rem;
    font-weight: 600;

    margin-top: 1.3rem;
    margin-bottom: 0.8rem;

    padding-bottom: 0.3rem;

    border-bottom:
        1px solid var(--border);
}


/* =====================================================
   METRIC CARDS
   ===================================================== */

[data-testid="stMetric"] {
    background-color:
        var(--navy-light);

    border:
        1px solid var(--border);

    border-radius: 0;

    padding:
        1rem 1.1rem;
}

[data-testid="stMetricLabel"] {
    color:
        var(--cream-muted) !important;

    font-family:
        Inter,
        sans-serif;

    font-size: 0.82rem !important;

    text-transform: uppercase;

    letter-spacing: 0.07em;
}

[data-testid="stMetricValue"] {
    font-family: "SFMono-Regular", Consolas, "Liberation Mono", monospace;

    font-size: 1.25rem !important;
}


/* =====================================================
   CAPTIONS
   ===================================================== */

.stCaption {
    color:
        var(--cream-muted) !important;
}


/* =====================================================
   DIVIDERS
   ===================================================== */

hr {
    border: none;

    border-top:
        1px solid var(--border);

    margin:
        2.5rem 0;
}


/* =====================================================
   ECONOMIC EVENTS
   ===================================================== */

.economic-event {

    padding:
        0.85rem 0 0.95rem 0;

    border-bottom:
        1px solid rgba(53, 64, 82, 0.65);

}


/* =====================================================
   EVENT HEADER
   ===================================================== */

.economic-event-top {

    display: grid;

    grid-template-columns:
        1.15fr 5.5fr 0.8fr;

    gap: 1.25rem;

    align-items: start;

}


/* =====================================================
   DATE / TIME
   ===================================================== */

.economic-event-date {

    font-family:
        Inter,
        sans-serif;

    font-size:
        0.68rem;

    font-weight:
        700;

    letter-spacing:
        0.08em;

    text-transform:
        uppercase;

    color:
        var(--cream);

}


.economic-event-date span {

    display: block;

    margin-top:
        0.25rem;

    font-size:
        0.74rem;

    font-weight:
        400;

    letter-spacing:
        0;

    text-transform:
        none;

    color:
        var(--cream-muted);

}


/* =====================================================
   EVENT NAME
   ===================================================== */

.economic-event-name {

    font-family:
        Georgia,
        "Times New Roman",
        serif;

    font-size:
        1.08rem;

    font-weight:
        600;

    line-height:
        1.2;

    color:
        var(--cream);

}

/* =====================================================
   ECONOMIC EVENT LINK
   ===================================================== */

.economic-event-link {
    color: var(--cream);
    text-decoration: none;
    cursor: pointer;
    transition: color 0.2s ease;
}

.economic-event-link:hover {
    color: var(--gold-light);
    text-decoration: underline;
}

.economic-event-title {

    margin-top:
        0.2rem;

    font-family:
        Inter,
        sans-serif;

    font-size:
        0.74rem;

    line-height:
        1.35;

    font-weight:
        400;

    color:
        var(--cream-muted);

}


/* =====================================================
   IMPACT
   ===================================================== */

.economic-event-impact {

    text-align:
        right;

    font-family:
        Inter,
        sans-serif;

    font-size:
        0.66rem;

    font-weight:
        700;

    letter-spacing:
        0.1em;

    color:
        var(--gold);

}


/* =====================================================
   CONSENSUS / PREVIOUS / ACTUAL
   ===================================================== */

.economic-event-details {

    display:
        grid;

    grid-template-columns:
        repeat(3, 1fr);

    gap:
        1.5rem;

    margin-top:
        0.7rem;

    padding-top:
        0.55rem;

    border-top:
        1px solid rgba(53, 64, 82, 0.35);

}


.economic-event-details span {

    display:
        block;

    font-family:
        Inter,
        sans-serif;

    font-size:
        0.62rem;

    font-weight:
        600;

    letter-spacing:
        0.09em;

    color:
        var(--cream-muted);

}


.economic-event-details strong {

    display:
        block;

    margin-top:
        0.15rem;

    font-family:
        Georgia,
        "Times New Roman",
        serif;

    font-size:
        0.88rem;

    font-weight:
        500;

    line-height:
        1.25;

    color:
        var(--cream);

}


/* =====================================================
   SOURCE
   ===================================================== */

.economic-event-source {

    margin-top:
        0.55rem;

    font-family:
        Inter,
        sans-serif;

    font-size:
        0.62rem;

    color:
        var(--cream-muted);

    opacity:
        0.8;

}


/* =====================================================
   NEWS
   ===================================================== */

.news-card {
    border-top:
        1px solid var(--border);

    padding:
        1rem 0 1.15rem 0;
}

.news-headline {
    display: inline-block;

    font-family:
        Georgia,
        "Times New Roman",
        serif;

    font-size: 1.25rem;

    line-height: 1.35;

    color:
        var(--cream);

    text-decoration: none;

    font-weight: 600;

    background: transparent;

    padding: 0;

    margin: 0;
}

.news-headline:hover {
    color:
        var(--gold-light);

    text-decoration: underline;
}

.news-meta {
    color:
        var(--cream-muted);

    font-size: 0.78rem;

    margin-top: 0.35rem;

    text-transform: uppercase;

    letter-spacing: 0.04em;
}

.news-description {
    color:
        #CDD3DF;

    font-size: 0.9rem;

    line-height: 1.5;

    margin-top: 0.55rem;

    max-width: 900px;
}


/* =====================================================
   BUTTONS
   ===================================================== */

.stButton > button {
    background-color:
        transparent;

    color:
        var(--cream);

    border:
        1px solid var(--border);

    border-radius: 0;

    font-family:
        Inter,
        sans-serif;

    transition:
        all 0.15s ease;
}

.stButton > button:hover {
    border-color:
        var(--gold);

    color:
        var(--gold-light);

    background-color:
        var(--navy-light);
}

/* =====================================================
   NEWS PAGINATION
   ===================================================== */

@media (max-width: 768px) {

    /* Keep pagination controls on one horizontal row */
    div[data-testid="stHorizontalBlock"]:has(
        button[key*="news_page_"]
    ) {
        flex-wrap: nowrap !important;
        overflow-x: auto;
        overflow-y: hidden;
        -webkit-overflow-scrolling: touch;
        scrollbar-width: none;
    }

    div[data-testid="stHorizontalBlock"]:has(
        button[key*="news_page_"]
    )::-webkit-scrollbar {
        display: none;
    }

}

/* =====================================================
   NEWS PAGINATION — ACTIVE PAGE
   ===================================================== */

/* Active/current page */
button[kind="primary"] {
    background-color: var(--gold) !important;
    border-color: var(--gold) !important;
    color: var(--navy) !important;
    font-weight: 700 !important;
}

/* =====================================================
   SELECTBOXES
   ===================================================== */

[data-baseweb="select"] > div {
    background-color:
        var(--navy-light);

    border-color:
        var(--border);

    border-radius: 0;

    color:
        var(--cream);
}


/* =====================================================
   EXPANDERS
   ===================================================== */

[data-testid="stExpander"] {
    background-color:
        var(--navy-light);

    border:
        1px solid var(--border);

    border-radius: 0;
}


/* =====================================================
   LINKS
   ===================================================== */

a {
    color:
        var(--gold-light);
}


/* =====================================================
   HIDE STREAMLIT BRANDING
   ===================================================== */

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

header {
    background-color:
        transparent;
}

/* =====================================================
   MOBILE OPTIMIZATION
   ===================================================== */

@media (max-width: 768px) {

    /* -----------------------------------------------
       HEADER
       ----------------------------------------------- */

    .tde-header {
        padding-top: 1.5rem;
        padding-bottom: 1rem;
        margin-bottom: 1.25rem;
    }

    .tde-header-row {
        flex-direction: column;
        align-items: flex-start;
        gap: 1rem;
    }

    .tde-title {
        font-size: 2.6rem;
    }

    .tde-subtitle {
        font-size: 0.95rem;
        margin-top: 0.7rem;
        line-height: 1.4;
    }

    .tde-market-status {
        text-align: left;
        padding-bottom: 0;
    }

    .tde-date {
        font-size: 0.85rem;
    }

    .market-open,
    .market-closed {
        font-size: 0.68rem;
    }

    .tde-market-description {
        font-size: 0.65rem;
    }


    /* -----------------------------------------------
       S&P 100 TICKER
       ----------------------------------------------- */

    .ticker-wrapper {
        margin-bottom: 1.25rem;
        padding: 0.55rem 0;
    }

    .ticker-item {
        font-size: 0.68rem;
        margin-right: 1.5rem;
    }


    /* -----------------------------------------------
       SECTION HEADERS
       ----------------------------------------------- */

    .section-header {
        margin-top: 2rem;
        margin-bottom: 0.8rem;
        gap: 0.65rem;
    }

    .section-header-title {
        font-size: 1.4rem;
    }

    .section-header-accent {
        font-size: 0.65rem;
    }


    /* -----------------------------------------------
       REGIONAL HEADERS
       ----------------------------------------------- */

    .region-title {
        font-size: 1.05rem;
        margin-top: 1rem;
        margin-bottom: 0.6rem;
    }


    /* -----------------------------------------------
       METRIC CARDS
       ----------------------------------------------- */

    [data-testid="stMetric"] {
        padding: 0.75rem 0.8rem;
    }

    [data-testid="stMetricValue"] {
        font-size: 1.35rem !important;
    }

    [data-testid="stMetricLabel"] {
        font-size: 0.7rem !important;
    }


    /* -----------------------------------------------
       NEWS
       ----------------------------------------------- */

    .news-card {
        padding: 0.85rem 0 1rem 0;
    }

    .news-headline {
        font-size: 1.05rem;
        line-height: 1.35;
    }

    .news-meta {
        font-size: 0.68rem;
        line-height: 1.4;
    }

    .news-description {
        font-size: 0.82rem;
        line-height: 1.45;
        margin-top: 0.45rem;
    }


    /* -----------------------------------------------
       ECONOMIC EVENTS
       ----------------------------------------------- */

    .economic-event {
        padding: 0.85rem 0 1rem 0;
    }

    .economic-event-top {
        grid-template-columns: 1fr;
        gap: 0.4rem;
    }

    .economic-event-impact {
        text-align: left;
        margin-top: 0.15rem;
    }

    .economic-event-details {
        grid-template-columns: repeat(3, 1fr);
        gap: 0.7rem;
    }

    .economic-event-name {
        font-size: 1rem;
    }

    .economic-event-title {
        font-size: 0.72rem;
    }


    /* -----------------------------------------------
       FOOTER
       ----------------------------------------------- */

    .tde-footer {
        margin-top: 2.5rem;
        padding-bottom: 1.5rem;
        font-size: 0.68rem;
    }

}

</style>
""",
    unsafe_allow_html=True
)

def get_us_market_status():

    eastern = ZoneInfo("America/New_York")
    now = datetime.now(eastern)
    current_time = now.time()

    market_open = time(9, 30)
    market_close = time(16, 0)
    premarket_start = time(4, 0)
    afterhours_end = time(20, 0)

    if now.weekday() >= 5:
        return ("CLOSED", now, "Markets closed")

    if market_open <= current_time < market_close:
        return ("OPEN", now, "Regular session")

    if premarket_start <= current_time < market_open:
        return ("PRE-MARKET", now, "Pre-market trading")

    if market_close <= current_time < afterhours_end:
        return ("AFTER HOURS", now, "After-hours trading")

    return ("CLOSED", now, "Markets closed")

# =========================================================
# HEADER
# =========================================================

# =========================================================
# LIVE MARKET STATUS
# =========================================================

market_status, market_time, market_description = (
    get_us_market_status()
)


date_display = market_time.strftime(
    "%A, %B %d, %Y"
)


status_class = (
    "market-open"
    if market_status == "OPEN"
    else "market-closed"
)


# =========================================================
# HEADER
# =========================================================

header_html = (
    '<div class="tde-header">'

    '<div class="tde-header-row">'

    '<div>'

    '<div class="tde-title">'
    'The Daily <span>Eagle</span>'
    '</div>'

    '<div class="tde-subtitle">'
    'Every number on this page today, '
    'sectioned like the morning paper.'
    '</div>'

    '</div>'

    '<div class="tde-market-status">'

    f'<div class="tde-date">'
    f'{date_display}'
    f'</div>'

    f'<div class="{status_class}">'
    f'US MARKETS: {market_status}'
    f'</div>'

    f'<div class="tde-market-description">'
    f'{market_description}'
    f'</div>'

    '</div>'

    '</div>'

    '</div>'
)


st.markdown(
    header_html,
    unsafe_allow_html=True
)

# =========================================================
# S&P 100 TICKER TAPE
# =========================================================

ticker_data = get_sp100_ticker_data()


if not ticker_data.empty:

    ticker_items = []

    for _, row in ticker_data.iterrows():

        ticker = row["ticker"]

        price = row["price"]

        change = row["change_pct"]


        if pd.notna(change):

            change_text = f"{change:+.2f}%"

            if change > 0:
                change_class = "up"

            elif change < 0:
                change_class = "down"

            else:
                change_class = "flat"

        else:

            change_text = "N/A"
            change_class = "flat"


        ticker_items.append(
            f'<span class="ticker-item">'
            f'<strong>{ticker}</strong> '
            f'{price:,.2f} '
            f'<span class="ticker-change {change_class}">'
            f'{change_text}'
            f'</span>'
            f'</span>'
        )


    ticker_string = (
        " · ".join(ticker_items)
    )


    # Duplicate the content so the animation
    # loops continuously.

    ticker_html = (
        '<div class="ticker-wrapper">'
        '<div class="ticker-track">'

        f'<div class="ticker-content">'
        f'{ticker_string}'
        f'</div>'

        f'<div class="ticker-content">'
        f'{ticker_string}'
        f'</div>'

        '</div>'
        '</div>'
    )


    st.markdown(
        ticker_html,
        unsafe_allow_html=True
    )

# =========================================================
# GLOBAL EQUITY MARKETS
# =========================================================

st.markdown(
    '<div class="section-header">'
    '<div class="section-header-title">'
    'Global Equity Markets'
    '</div>'
    '<div class="section-header-accent">'
    'Markets'
    '</div>'
    '</div>',
    unsafe_allow_html=True
)


for region, instruments in INDICES.items():

    st.markdown(
        f'<div class="region-title">{region}</div>',
        unsafe_allow_html=True
    )

    market_data = get_market_data(instruments)

    columns = st.columns(4)

    for i, row in market_data.iterrows():

        with columns[i % 4]:

            value = row["value"]
            change = row["change_pct"]

            if pd.notna(value):

                st.metric(
                    label=row["name"],
                    value=f"{value:,.2f}",
                    delta=(
                        f"{change:+.2f}%"
                        if pd.notna(change)
                        else "N/A"
                    )
                )

                st.caption(
                    f"Source: {row['source']}"
                )

            else:

                st.metric(
                    label=row["name"],
                    value="N/A"
                )

                st.caption(
                    f"Source: {row['source']}"
                )


# =========================================================
# US TREASURY YIELDS
# =========================================================

st.divider()

st.markdown(
    '<div class="section-header">'
    '<div class="section-header-title">'
    'US Treasury Yields'
    '</div>'
    '<div class="section-header-accent">'
    'Rates'
    '</div>'
    '</div>',
    unsafe_allow_html=True
)


treasury_data = get_treasury_data()

columns = st.columns(4)

for i, row in treasury_data.iterrows():

    with columns[i % 4]:

        if pd.notna(row["yield"]):

            st.metric(
                label=f"US Treasury {row['maturity']}",
                value=f"{row['yield']:.2f}%",
                delta=(
                    f"{row['change_bp']:+.1f} bp"
                    if pd.notna(row["change_bp"])
                    else "N/A"
                )
            )

            st.caption(
                f"Source: {row['source']} · {row['date']}"
            )

        else:

            st.metric(
                label=f"US Treasury {row['maturity']}",
                value="N/A"
            )

            st.caption(
                f"Source: {row['source']}"
            )


# =========================================================
# YIELD CURVE
# =========================================================

st.subheader("Yield Curve")

yield_curve = create_yield_curve(
    treasury_data
)

st.plotly_chart(
    yield_curve,
    use_container_width=True
)


# =========================================================
# KEY TREASURY SPREADS
# =========================================================

st.subheader("Key Treasury Spreads")

try:

    yields = dict(
        zip(
            treasury_data["maturity"],
            treasury_data["yield"]
        )
    )

    spread_2s10s = (
        yields["10Y"]
        - yields["2Y"]
    ) * 100

    spread_5s30s = (
        yields["30Y"]
        - yields["5Y"]
    ) * 100

    columns = st.columns(2)

    with columns[0]:

        st.metric(
            "2s10s",
            f"{spread_2s10s:+.1f} bp"
        )

        st.caption(
            "10Y Treasury yield minus 2Y Treasury yield"
        )

    with columns[1]:

        st.metric(
            "5s30s",
            f"{spread_5s30s:+.1f} bp"
        )

        st.caption(
            "30Y Treasury yield minus 5Y Treasury yield"
        )

except Exception:

    st.warning(
        "Treasury spread data is currently unavailable."
    )


# =========================================================
# COMMODITIES
# =========================================================

st.divider()

st.markdown(
    '<div class="section-header">'
    '<div class="section-header-title">'
    'Major Commodities'
    '</div>'
    '<div class="section-header-accent">'
    'Prices'
    '</div>'
    '</div>',
    unsafe_allow_html=True
)


commodity_data = get_commodity_data()

columns = st.columns(3)

for i, row in commodity_data.iterrows():

    with columns[i % 3]:

        if pd.notna(row["value"]):

            st.metric(
                label=row["name"],
                value=f"{row['value']:,.2f}",
                delta=(
                    f"{row['change_pct']:+.2f}%"
                    if pd.notna(row["change_pct"])
                    else "N/A"
                )
            )

            st.caption(
                f"Source: {row['source']}"
            )

        else:

            st.metric(
                label=row["name"],
                value="N/A"
            )

            st.caption(
                f"Source: {row['source']}"
            )


# =========================================================
# ECONOMIC EVENTS
# =========================================================

st.divider()

st.markdown(
    '<div class="section-header">'
    '<div class="section-header-title">'
    'Economic Events'
    '</div>'
    '<div class="section-header-accent">'
    'Macro'
    '</div>'
    '</div>',
    unsafe_allow_html=True
)


economic_data = get_economic_calendar()


if economic_data.empty:

    st.warning(
        "Economic calendar data is currently unavailable."
    )

else:

    # -----------------------------------------------------
    # FILTERS
    # -----------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        impact_options = [
            "All",
            "high",
            "medium",
            "low"
        ]

        selected_impact = st.selectbox(
            "Impact",
            impact_options,
            key="economic_impact"
        )

    with col2:

        categories = [
            "All"
        ] + sorted(
            economic_data["category"]
            .dropna()
            .unique()
            .tolist()
        )

        selected_category = st.selectbox(
            "Category",
            categories,
            key="economic_category"
        )


    # -----------------------------------------------------
    # APPLY FILTERS
    # -----------------------------------------------------

    filtered_data = economic_data.copy()


    if selected_impact != "All":

        filtered_data = filtered_data[
            filtered_data["impact"]
            .fillna("")
            .str.lower()
            == selected_impact
        ]


    if selected_category != "All":

        filtered_data = filtered_data[
            filtered_data["category"]
            == selected_category
        ]


    # -----------------------------------------------------
    # SORT
    # -----------------------------------------------------

    filtered_data = filtered_data.sort_values(
        by=[
            "date",
            "time_et"
        ],
        na_position="last"
    )


    # -----------------------------------------------------
    # SHOW / HIDE STATE
    # -----------------------------------------------------

    if "show_all_events" not in st.session_state:

        st.session_state.show_all_events = False


    # -----------------------------------------------------
    # FIVE EVENTS BY DEFAULT
    # -----------------------------------------------------

    if st.session_state.show_all_events:

        events_to_display = filtered_data

    else:

        events_to_display = filtered_data.head(5)


   # -----------------------------------------------------
    # DISPLAY EVENTS
    # -----------------------------------------------------

    event_blocks = []


    for _, row in events_to_display.iterrows():

        event_date = row["date"]

        event_time = row["time_et"]

        if (
            pd.isna(event_time)
            or event_time is None
            or str(event_time).strip() == ""
        ):

            event_time = "All day"


        impact = (
            str(row["impact"]).upper()
            if pd.notna(row["impact"])
            else "N/A"
        )


        event_name = (
            str(row["event"])
            if pd.notna(row["event"])
            else "Economic Event"
        )


        title = (
            str(row["title"])
            if pd.notna(row["title"])
            else ""
        )


        consensus = (
            str(row["consensus"])
            if pd.notna(row["consensus"])
            else "—"
        )


        previous = (
            str(row["previous"])
            if pd.notna(row["previous"])
            else "—"
        )


        actual = (
            str(row["actual"])
            if pd.notna(row["actual"])
            else "—"
        )


        event_url = (
            str(row["source_url"])
            if "source_url" in row.index
            and pd.notna(row["source_url"])
            else ""
        )


        # -------------------------------------------------
        # EVENT HEADLINE LINK
        # -------------------------------------------------

        if event_url:

            event_name_html = (
                f'<a '
                f'class="economic-event-link" '
                f'href="{event_url}" '
                f'target="_blank" '
                f'rel="noopener noreferrer">'
                f'{event_name}'
                f'</a>'
            )

        else:

            event_name_html = (
                f'<span class="economic-event-link">'
                f'{event_name}'
                f'</span>'
            )


        # -------------------------------------------------
        # BUILD EVENT
        # -------------------------------------------------

        event_html = (

            '<div class="economic-event">'

            '<div class="economic-event-top">'

            f'<div class="economic-event-date">'
            f'{event_date}'
            f'<span>{event_time}</span>'
            f'</div>'

            f'<div class="economic-event-name">'
            f'{event_name_html}'

            f'<div class="economic-event-title">'
            f'{title}'
            f'</div>'

            f'</div>'

            f'<div class="economic-event-impact">'
            f'{impact}'
            f'</div>'

            '</div>'

            '<div class="economic-event-details">'

            f'<div>'
            f'<span>CONSENSUS</span>'
            f'<strong>{consensus}</strong>'
            f'</div>'

            f'<div>'
            f'<span>PREVIOUS</span>'
            f'<strong>{previous}</strong>'
            f'</div>'

            f'<div>'
            f'<span>ACTUAL</span>'
            f'<strong>{actual}</strong>'
            f'</div>'

            '</div>'

            '</div>'
        )


        event_blocks.append(event_html)


# -------------------------------------------------
# RENDER ALL EVENTS TOGETHER
# -------------------------------------------------

if event_blocks:

    st.markdown(
        "".join(event_blocks),
        unsafe_allow_html=True
    )
    # -----------------------------------------------------
    # SHOW MORE / SHOW LESS
    # -----------------------------------------------------

    if len(filtered_data) > 5:

        if not st.session_state.show_all_events:

            if st.button(
                f"Show more ({len(filtered_data) - 5} additional events)",
                use_container_width=True,
                key="show_more_economic_events"
            ):

                st.session_state.show_all_events = True

                st.rerun()

        else:

            if st.button(
                "Show less",
                use_container_width=True,
                key="show_less_economic_events"
            ):

                st.session_state.show_all_events = False

                st.rerun()


# =========================================================
# NEWS
# =========================================================

st.divider()

st.markdown(
    '<div class="section-header">'
    '<div class="section-header-title">'
    'News'
    '</div>'
    '<div class="section-header-accent">'
    'The Morning Brief'
    '</div>'
    '</div>',
    unsafe_allow_html=True
)


news_data = get_news()


if news_data.empty:

    st.warning(
        "News data is currently unavailable."
    )

else:

    news_categories = [
        "Markets",
        "Macro & Central Banks",
        "Investment Banking & M&A",
        "Technology",
        "Energy & Commodities",
        "Financial Services",
        "Miscellaneous"
    ]


    # =====================================================
    # NEWS DISPLAY FUNCTION
    # =====================================================

    def display_news_section(
        category,
        data
    ):

        category_data = data[
            data["category"]
            == category
        ].copy()


        if category_data.empty:

            return


        st.markdown(
            f'<div class="region-title">{category}</div>',
            unsafe_allow_html=True
        )


        # -------------------------------------------------
        # SESSION STATE KEYS
        # -------------------------------------------------

        category_key = (
            category
            .lower()
            .replace(" ", "_")
            .replace("&", "and")
        )

        page_key = (
            f"news_page_{category_key}"
        )


        if page_key not in st.session_state:

            st.session_state[
                page_key
            ] = 1


        page_size = 5


        # -------------------------------------------------
        # ALL STORIES AVAILABLE THROUGH PAGINATION
        # -------------------------------------------------

        visible_data = category_data.copy()

        # -------------------------------------------------
        # TOTAL PAGES
        # -------------------------------------------------

        total_pages = max(
            1,
            (
                len(visible_data)
                + page_size
                - 1
            )
            // page_size
        )


        if (
            st.session_state[page_key]
            > total_pages
        ):

            st.session_state[
                page_key
            ] = total_pages


        current_page = (
            st.session_state[
                page_key
            ]
        )


        start = (
            current_page - 1
        ) * page_size


        end = (
            start
            + page_size
        )


        page_data = visible_data.iloc[
            start:end
        ]


        # -------------------------------------------------
        # DISPLAY STORIES
        # -------------------------------------------------

        for _, row in page_data.iterrows():

            title = row["title"]

            url = row["url"]

            source = row["source"]

            description = row["description"]

            published = row["published"]


            # -------------------------------------------------
            # PUBLICATION TIME
            # -------------------------------------------------

            if pd.notna(published):

                try:

                    published_text = (
                        published.strftime(
                            "%b %d, %Y · %I:%M %p UTC"
                        )
                    )

                except Exception:

                    published_text = str(
                        published
                    )

            else:

                published_text = (
                    "Publication time unavailable"
                )


            # -------------------------------------------------
            # NEWS CARD
            # -------------------------------------------------

            st.markdown(
                '<div class="news-card">',
                unsafe_allow_html=True
            )


            # -------------------------------------------------
            # CLICKABLE HEADLINE
            # -------------------------------------------------

            if url:

                st.markdown(
                    f'<a class="news-headline" href="{url}" target="_blank">{title}</a>',
                    unsafe_allow_html=True
                )

            else:

                st.markdown(
                    f'<div class="news-headline">{title}</div>',
                    unsafe_allow_html=True
                )


            # -------------------------------------------------
            # SOURCE / TIME
            # -------------------------------------------------

            st.markdown(
                f'<div class="news-meta">'
                f'{source} · {published_text}'
                f'</div>',
                unsafe_allow_html=True
            )


            # -------------------------------------------------
            # DESCRIPTION
            # -------------------------------------------------

            if description:

                description_text = str(
                    description
                )


                if len(description_text) > 280:

                    description_text = (
                        description_text[:280]
                        + "..."
                    )


                st.markdown(
                    f'<div class="news-description">'
                    f'{description_text}'
                    f'</div>',
                    unsafe_allow_html=True
                )


            st.markdown(
                '</div>',
                unsafe_allow_html=True
            )


        # -------------------------------------------------
        # PAGINATION
        # -------------------------------------------------

        if total_pages > 1:

            max_visible_pages = 6

            # Determine which page numbers to display
            if total_pages <= max_visible_pages:

                page_numbers = list(
                    range(1, total_pages + 1)
                )

            elif current_page <= 3:

                page_numbers = list(
                    range(1, max_visible_pages + 1)
                )

            elif current_page >= total_pages - 2:

                page_numbers = list(
                    range(
                        total_pages - max_visible_pages + 1,
                        total_pages + 1
                    )
                )

            else:

                page_numbers = list(
                    range(
                        current_page - 2,
                        current_page + 4
                    )
                )


            # Previous + page numbers + next
            pagination_columns = st.columns(
                len(page_numbers) + 2
            )


            # -------------------------------------------------
            # PREVIOUS
            # -------------------------------------------------

            with pagination_columns[0]:

                if st.button(
                    "‹",
                    key=f"{page_key}_prev",
                    disabled=(
                        current_page == 1
                    )
                ):

                    st.session_state[
                        page_key
                    ] -= 1

                    st.rerun()


            # -------------------------------------------------
            # PAGE NUMBERS
            # -------------------------------------------------

            for index, page_number in enumerate(
                page_numbers,
                start=1
            ):

                with pagination_columns[index]:

                    if st.button(
                        str(page_number),
                        key=(
                            f"{page_key}_"
                            f"{page_number}"
                        ),
                        type=(
                            "primary"
                            if page_number == current_page
                            else "secondary"
                        )
                    ):

                        st.session_state[
                            page_key
                        ] = page_number

                        st.rerun()


            # -------------------------------------------------
            # NEXT
            # -------------------------------------------------

            with pagination_columns[-1]:

                if st.button(
                    "›",
                    key=f"{page_key}_next",
                    disabled=(
                        current_page == total_pages
                    )
                ):

                    st.session_state[
                        page_key
                    ] += 1

                    st.rerun()



        st.markdown(
            "<br>",
            unsafe_allow_html=True
        )


    # =====================================================
    # DISPLAY NEWS CATEGORIES
    # =====================================================

    for category in news_categories:

        display_news_section(
            category,
            news_data
        )


# =========================================================
# RAW MARKET DATA
# =========================================================

with st.expander("View market data"):

    st.dataframe(
        market_data,
        use_container_width=True
    )


st.markdown(
    '<div class="tde-footer">Developed by Samiksh using 5.6 Luna, VS Code and Streamlit</div>',
    unsafe_allow_html=True
)