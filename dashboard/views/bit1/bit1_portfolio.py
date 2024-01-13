from pandas import Timestamp
from datetime import datetime, timedelta
from dash import dcc, html
from dash.dependencies import Input, Output
import pymongo
import pandas as pd
import plotly.graph_objs as go
import os
from dotenv import load_dotenv
from maindash import app

load_dotenv()
MONGODB_CONNECTION = os.getenv('MONGODB_CONNECTION')

coinIds = ["yield-guild-games", "alethea-artificial-liquid-intelligence-token",
           "immutable-x", "rainbow-token-2", "superfarm", "matic-network", "sipher", 
           "blackpool-token", "vcore"]

labels = ["YGG", "ALI", "IMX", "RBW", "SUPER", "MATIC", "SIPHER", "BPT", "VCORE"]

client = pymongo.MongoClient(MONGODB_CONNECTION)
db = client["historical_price_data"]

df = pd.DataFrame(columns=['time'])
df.set_index('time', inplace=True)

for index, coin in enumerate(coinIds):
    col = db[coinIds[index]]
    cursor = col.find({}, {"_id":0, "time":1, "eth_value":1})
    li = list(cursor)
    df1 = pd.DataFrame(li)
    df1['time'] = pd.to_datetime(df1["time"], unit="ms")
    coin_name = coinIds[index]
    df1.rename(columns={"eth_value": coin_name}, inplace=True)
    df1.set_index('time', inplace=True)
    df1.sort_index(inplace=True)
    df = pd.merge(df, df1, on='time', how='outer')

df.sort_index(inplace=True)

def display_bit1_portfolio():
    return html.Div([
        dcc.Graph(
            id="bit1_portfolio_fig", 
            config={"displayModeBar": False},
            style={'height': 700} 
        ),
    ])

@app.callback(
    Output("bit1_portfolio_fig", "figure"),
    Input("bit1_portfolio_fig", "relayoutData"),
)
def update_chart(rng):
    traces = []

    filtered_data = df
    # Check if DataFrame's index is timezone-aware and get its timezone
    end_date = datetime.now()
    start_date = end_date - timedelta(days=1 * 365)

    # If there's a range selection from user, update the start and end dates
    if rng and "xaxis.range[0]" in rng.keys():
        start_date = pd.to_datetime(rng.get("xaxis.range[0]"))
        end_date = pd.to_datetime(rng.get("xaxis.range[1]"))

    # Filter the data based on the calculated range
    mask = (df.index >= start_date) & (df.index <= end_date)
    filtered_data = df.loc[mask]
    
    # Calculate min and max values for y-axis across all columns
    y_min = filtered_data.min().min()
    y_max = filtered_data.max().max()

    for index, col in enumerate(filtered_data):
        series = filtered_data[col]
        first = series.index.get_loc(series.first_valid_index())
        reference_value = series[first]
        indexed_series = series.div(reference_value) * 100 - 100
        traces.append(go.Scatter(x=indexed_series.index, y=indexed_series, name=labels[index]))

    layout = dict(
        title=dict(
            text="BIT1 Portfolio (ETH indexed)",
            x=0.01,
            xanchor="left",
        ),
        margin=dict(l=20,r=70,t=80,b=30,pad=4),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            title=""
        ),
        yaxis=dict(
            tickformat=".0f",
            fixedrange=True,
            side="right",
            ticksuffix="%",
            showline=True,
            linecolor="grey",
            title="",
        ),
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(count=2, label="2y", step="year", stepmode="backward"),
                    dict(count=3, label="3y", step="year", stepmode="backward"),
                    dict(step="all")
                ])
            ),
            type="date",
            showline=True,
            linecolor="grey",
            title="",
            range=[start_date, end_date],
        ),
        plot_bgcolor="white",
        shapes=[
            dict(
                type="line",
                xref="paper",
                yref="y",
                x0=0,
                y0=0,
                x1=1,
                y1=0,
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
