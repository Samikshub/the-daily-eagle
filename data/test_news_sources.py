import feedparser

from data.news_sources import NEWS_SOURCES


for category, sources in NEWS_SOURCES.items():

    print("\n" + "=" * 60)
    print(category.upper())
    print("=" * 60)

    for source in sources:

        name = source["name"]
        url = source["url"]

        if not url:

            print(f"{name}: NEEDS FEED URL")
            continue

        try:

            feed = feedparser.parse(url)

            print(
                f"{name}: "
                f"{len(feed.entries)} articles"
            )

        except Exception as e:

            print(
                f"{name}: ERROR - {e}"
            )