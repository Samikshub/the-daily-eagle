import yfinance as yf
import pandas as pd
import streamlit as st

from config.assets import SP100


@st.cache_data(ttl=60)
def get_sp100_ticker_data():

    try:

        data = yf.download(
            SP100,
            period="2d",
            interval="1d",
            group_by="ticker",
            auto_adjust=False,
            progress=False,
            threads=True
        )

        results = []

        for ticker in SP100:

            try:

                ticker_data = data[ticker]

                ticker_data = ticker_data.dropna(
                    subset=["Close"]
                )

                if ticker_data.empty:
                    continue

                latest = float(
                    ticker_data["Close"].iloc[-1]
                )

                if len(ticker_data) >= 2:

                    previous = float(
                        ticker_data["Close"].iloc[-2]
                    )

                    change_pct = (
                        (latest / previous) - 1
                    ) * 100

                else:

                    change_pct = None


                results.append(
                    {
                        "ticker": ticker,
                        "price": latest,
                        "change_pct": change_pct,
                    }
                )

            except Exception:

                continue


        return pd.DataFrame(results)


    except Exception:

        return pd.DataFrame()