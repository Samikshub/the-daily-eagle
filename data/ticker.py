import yfinance as yf
import pandas as pd
import streamlit as st

from config.assets import SP100


@st.cache_data(ttl=60)
def get_sp100_ticker_data():

    results = []

    for ticker in SP100:

        try:

            stock = yf.Ticker(ticker)

            info = stock.info

            current_price = info.get("regularMarketPrice")
            previous_close = info.get("regularMarketPreviousClose")

            if current_price is None:
                continue

            current_price = float(current_price)

            if previous_close is not None:
                previous_close = float(previous_close)

                change_pct = (
                    (current_price / previous_close) - 1
                ) * 100

            else:
                change_pct = None

            results.append(
                {
                    "ticker": ticker,
                    "price": current_price,
                    "change_pct": change_pct,
                }
            )

        except Exception:
            continue

    return pd.DataFrame(results)