import plotly.graph_objects as go
import pandas as pd


def create_yield_curve(treasury_data):

    maturities = [
        "2Y",
        "3Y",
        "5Y",
        "7Y",
        "10Y",
        "20Y",
        "30Y"
    ]

    curve_data = treasury_data[
        treasury_data["maturity"].isin(maturities)
    ].copy()

    curve_data["maturity"] = pd.Categorical(
        curve_data["maturity"],
        categories=maturities,
        ordered=True
    )

    curve_data = curve_data.sort_values("maturity")

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=curve_data["maturity"],
            y=curve_data["yield"],
            mode="lines+markers",
            name="Treasury Yield"
        )
    )

    fig.update_layout(
        title="US Treasury Yield Curve",
        xaxis_title="Maturity",
        yaxis_title="Yield (%)",
        height=450,
        template="plotly_dark",
        hovermode="x unified"
    )

    return fig