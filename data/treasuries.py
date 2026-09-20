import pandas as pd
import streamlit as st

from config.assets import TREASURIES


@st.cache_data(ttl=300)
def get_treasury_data():

    results = []

    for maturity, series in TREASURIES.items():

        try:

            url = (
                "https://fred.stlouisfed.org/graph/"
                f"fredgraph.csv?id={series}"
            )

            data = pd.read_csv(url)

            # Remove missing observations
            data = data[data[series] != "."]

            latest = float(data[series].iloc[-1])

            if len(data) >= 2:
                previous = float(data[series].iloc[-2])
                change = (latest - previous) * 100
            else:
                change = None

            results.append({
                "maturity": maturity,
                "yield": latest,
                "change_bp": change,
                "series": series,
                "source": "FRED / Federal Reserve",
                "date": data["observation_date"].iloc[-1]
            })

        except Exception as e:

            results.append({
                "maturity": maturity,
                "yield": None,
                "change_bp": None,
                "series": series,
                "source": "FRED / Federal Reserve",
                "date": None,
                "error": str(e)
            })

    return pd.DataFrame(results)