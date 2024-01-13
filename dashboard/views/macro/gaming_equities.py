from dash import dcc, html
import yfinance as yf
from maindash import app
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from datetime import datetime

tickers = ["^GSPC", "NERD", "GAMR", "HERO", "ESPO"]

df = yf.download(
    tickers, 
    start="2019-05-15", 
    end=datetime.now(), 
    interval="1d",
)

df = df.filter(regex="Adj Close")
df = df.dropna()
df = df["Adj Close"]
df = df.rename(columns={'^GSPC': 'S&P500'})

colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"]

def display_gaming_equities():
    return html.Div(
        children=dcc.Graph(
            id="gaming_equities_fig", 
            config={"displayModeBar": False},
        ),
    )

@app.callback(
    Output("gaming_equities_fig", "figure"),
    Input("gaming_equities_fig", "relayoutData"),
)
def update_chart(rng):
    if rng and "xaxis.range[0]" in rng.keys():
        lower = rng.get("xaxis.range[0]")
        upper = rng.get("xaxis.range[1]")

        range = ((df.index >= lower) & (df.index <= upper))
        filtered_df = df.loc[range, :]       
        reference_value = filtered_df.iloc[0]        
        indexed_df = filtered_df.div(reference_value) * 100 - 100        
    else:
        reference_value = df.iloc[0]
        indexed_df = df.div(reference_value) * 100 - 100

    traces = []
    for i, col in enumerate(indexed_df.columns):
        traces.append(go.Scatter(
            x=indexed_df.index, 
            y=indexed_df[col], 
            mode='lines', 
            name=col,
            line=dict(color=colors[i % len(colors)]) # Cycle through colors
        ))

    layout = dict(
        title=dict(
            text="Gaming Equities",
            x=0.03,
            xanchor="left",
        ),
        colorway=["#17B897"],
        plot_bgcolor="white",
        margin=dict(l=20,r=50,t=80,b=20,pad=4),
        yaxis=dict(
            tickformat=".f", 
            fixedrange=True,
            side="right",
            ticksuffix="%",
            showline=True,
            linecolor="grey",
            title=""
        ),
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(step="all")
                ])
            ),
            type="date",
            showline=True,
            linecolor="grey",
            title=""
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            title=""
        ),
        shapes=[
            dict(type="line", xref="paper", yref="y", x0=0, y0=0, x1=1, y1=0,          
                line=dict(
                    color="lightgrey",
                    width=0.5,
                    dash="dash"
                ),
            ),
        ]
    )

    fig = dict(data=traces, layout=layout)
    return fig
