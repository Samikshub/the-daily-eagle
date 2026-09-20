import yfinance as yf
import pandas as pd
import streamlit as st


@st.cache_data(ttl=60)
def get_market_data(instruments):

    results = []

    for name, ticker in instruments.items():

        try:
            data = yf.Ticker(ticker).history(period="2d")

            if data.empty:
                continue

            latest = data["Close"].iloc[-1]

            if len(data) >= 2:
                previous = data["Close"].iloc[-2]
                change_pct = ((latest / previous) - 1) * 100
            else:
                change_pct = None

            results.append({
                "name": name,
                "ticker": ticker,
                "value": latest,
                "change_pct": change_pct,
                "source": "Yahoo Finance",
                "timestamp": data.index[-1]
            })

        except Exception as e:

            results.append({
                "name": name,
                "ticker": ticker,
                "value": None,
                "change_pct": None,
                "source": "Yahoo Finance",
                "timestamp": None,
                "error": str(e)
            })

    return pd.DataFrame(results)