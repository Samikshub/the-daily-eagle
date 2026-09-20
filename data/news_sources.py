NEWS_SOURCES = {

    # ========================================================
    # FINANCE / MARKETS
    # ========================================================

    "markets": [

    {
        "name": "Bloomberg",
        "type": "rss",
        "url": "https://feeds.bloomberg.com/markets/news.rss",
        "priority": 5,
    },

    {
        "name": "Wall Street Journal",
        "type": "rss",
        "url": "https://feeds.content.dowjones.io/public/rss/RSSMarketsMain",
        "priority": 5,
    },

    {
        "name": "Financial Times",
        "type": "rss",
        "url": "https://www.ft.com/markets?format=rss",
        "priority": 5,
    },

    {
        "name": "CNBC Markets",
        "type": "rss",
        "url": "https://www.cnbc.com/id/100003114/device/rss/rss.html",
        "priority": 4,
    },

    {
        "name": "Yahoo Finance",
        "type": "rss",
        "url": "https://finance.yahoo.com/news/rssindex",
        "priority": 3,
    },

    {
        "name": "MarketWatch",
        "type": "rss",
        "url": "https://feeds.marketwatch.com/marketwatch/topstories/",
        "priority": 3,
    },
],


    # ========================================================
    # BUSINESS
    # ========================================================

    "business": [

        {
            "name": "Morning Brew",
            "type": "rss",
            "url": None,
            "priority": 4,
        },

        {
            "name": "Forbes Business",
            "type": "rss",
            "url": "https://www.forbes.com/business/feed/",
            "priority": 3,
        },

        {
            "name": "Business Insider",
            "type": "rss",
            "url": "https://www.businessinsider.com/rss",
            "priority": 3,
        },
    ],


    # ========================================================
    # TECHNOLOGY
    # ========================================================

   "technology": [

    {
        "name": "Bloomberg Technology",
        "type": "rss",
        "url": "https://feeds.bloomberg.com/technology/news.rss",
        "priority": 5,
    },

    {
        "name": "CNBC Technology",
        "type": "rss",
        "url": "https://www.cnbc.com/id/19854910/device/rss/rss.html",
        "priority": 4,
    },

    {
        "name": "TechCrunch",
        "type": "rss",
        "url": "https://techcrunch.com/feed/",
        "priority": 3,
    },
],

    # ========================================================
    # MACRO / PRIMARY SOURCES
    # ========================================================

    "macro": [

        {
            "name": "Federal Reserve",
            "type": "rss",
            "url": "https://www.federalreserve.gov/feeds/press_all.xml",
            "priority": 5,
        },

        {
            "name": "SEC",
            "type": "rss",
            "url": "https://www.sec.gov/news/pressreleases.rss",
            "priority": 5,
        },
    ],


    # ========================================================
    # ENERGY / COMMODITIES
    # ========================================================

    "commodities": [

        {
            "name": "CNBC Energy",
            "type": "rss",
            "url": "https://www.cnbc.com/id/19836768/device/rss/rss.html",
            "priority": 4,
        },
    ],


    # ========================================================
    # MISCELLANEOUS
    # ========================================================

    "misc": [

        {
            "name": "Morning Brew",
            "type": "rss",
            "url": None,
            "priority": 4,
        },

        {
            "name": "BBC News",
            "type": "rss",
            "url": "https://feeds.bbci.co.uk/news/rss.xml",
            "priority": 2,
        },

        {
            "name": "BBC Business",
            "type": "rss",
            "url": "https://feeds.bbci.co.uk/news/business/rss.xml",
            "priority": 3,
        },
    ],
}