from maindash import app
from dash.dependencies import Input, Output
from dash import dcc
from dash import html
import pymongo
import pandas as pd
import plotly.express as px 
import datetime as dt
import plotly.graph_objects as go
import os
from dotenv import load_dotenv

load_dotenv()
MONGODB_CONNECTION = os.getenv('MONGODB_CONNECTION')

coinIds = ["yield-guild-games", "alethea-artificial-liquid-intelligence-token",
    "immutable-x", "rainbow-token-2", "superfarm", "matic-network", "sipher", "blackpool-token"]

results = [None] * len(coinIds)

client = pymongo.MongoClient(MONGODB_CONNECTION)
db = client["historical_price_data"]

df = pd.DataFrame(columns=['time'])
df.set_index('time', inplace=True)

for index, coin in enumerate(coinIds):
    col = db[coinIds[index]]
    cursor = col.find({}, {"_id":0, "time":1, "usd_value":1})
    li = list(cursor)
    df1 = pd.DataFrame(li)
    df1['time'] = pd.to_datetime(df1["time"], unit="ms")
    coin_name = (coinIds[index])
    df1.rename(columns={"usd_value":coin_name}, inplace = True)
    df1.set_index('time', inplace=True)
    df1.sort_index(inplace=True)
    df = pd.merge(df, df1, on='time', how='outer')

df.sort_index(inplace=True)   

def display_bit1_portfolio():
    return html.Div(
        children=dcc.Graph(
            id="bit1_portfolio_fig", 
            config={"displayModeBar": False},
        ),
    )

@app.callback(
    Output("bit1_portfolio_fig", "figure"),
    Input("bit1_portfolio_fig", "relayoutData"),
)
def update_chart(rng):

    fig = go.Figure()
    if rng and "xaxis.range[0]" in rng.keys():

        lower = rng.get(list(rng.keys())[0])
        upper = rng.get(list(rng.keys())[1])

        range = ((df.index >= lower) & (df.index  <= upper))
        filtered_df = df.loc[range, :]

        for col in filtered_df:
            series = filtered_df[col]
            print(series)
            first = series.index.get_loc(series.first_valid_index())
            reference_value = series[first]
            print("reference value: ", reference_value)
            indexed_series = series.div(reference_value) * 100 - 100  
            fig.add_trace(go.Scatter(x=indexed_series.index, y=indexed_series))

    else:

        for col in df:
            series = df[col]
            print(series)
            # first valid position, i.e. first non-NaN value
            first = series.index.get_loc(series.first_valid_index())
            print("first valid index: ", first)
            reference_value = series[first]
            print("reference value: ", reference_value)
            indexed_series = series.div(reference_value) * 100 - 100  
            fig.add_trace(go.Scatter(x=indexed_series.index, y=indexed_series))
        
    fig.update_layout(
        title=dict(
                text="BIT1 Portfolio",
                x=0.08,
                xanchor="left",
            ),
        legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                title=""
            ),
        yaxis=dict(
                tickformat=".2f", 
                fixedrange= True,
                side="right",
                ticksuffix="%",
                showline=True,
                linecolor="grey",
                title=""
            ),
        xaxis=dict(
                rangeselector=dict(
                    buttons=list([
                        dict(count=1,
                            label="1m",
                            step="month",
                            stepmode="backward"),
                        dict(count=6,
                            label="6m",
                            step="month",
                            stepmode="backward"),
                        dict(count=1,
                            label="YTD",
                            step="year",
                            stepmode="todate"),
                        dict(count=1,
                            label="1y",
                            step="year",
                            stepmode="backward"),
                        dict(step="all")
                    ])
                ),
                type="date",
                showline=True,
                linecolor="grey",
                title=""
            ),
        plot_bgcolor="white",       
    )

    fig.add_hline(y=0, line_dash="dash", line_color="black", line_width=0.5, opacity=0.7)
    return fig