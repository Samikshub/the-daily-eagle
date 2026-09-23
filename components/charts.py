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

    # Dynamic Y-axis range
    min_yield = curve_data["yield"].min()
    max_yield = curve_data["yield"].max()

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=curve_data["maturity"].str.replace(
                "Y", ""
            ).astype(int),

            y=curve_data["yield"],

            mode="lines+markers",

            name="Treasury Yield",

            line=dict(
                color="#C9A14B",
                width=2
            ),

            marker=dict(
                color="#C9A14B",
                size=7
            )
        )
    )

    fig.update_layout(
        title="US Treasury Yield Curve",

        height=450,

        plot_bgcolor="#0F1826",
        paper_bgcolor="#0F1826",

        font=dict(
            color="#EDE6D6"
        ),

        xaxis=dict(
            title="Maturity",

            tickmode="array",

            tickvals=[
                2,
                3,
                5,
                7,
                10,
                20,
                30
            ],

            ticktext=[
                "2Y",
                "3Y",
                "5Y",
                "7Y",
                "10Y",
                "20Y",
                "30Y"
            ],

            gridcolor="#354052",

            zerolinecolor="#354052"
        ),

        yaxis=dict(
            title="Yield (%)",

            gridcolor="#354052",

            zerolinecolor="#354052",

            tickformat=".1f",

            range=[
                min_yield - 0.1,
                max_yield + 0.1
            ]
        ),

        hovermode="x unified"
    )

    return fig