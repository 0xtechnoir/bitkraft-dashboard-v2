from maindash import app
from dash.dependencies import Input, Output
from dash import dcc, html
import pymongo
import pandas as pd
import plotly.graph_objs as go
import datetime as dt
import os
from dotenv import load_dotenv

load_dotenv()
MONGODB_CONNECTION = os.getenv('MONGODB_CONNECTION')

coinIds = ["karate-combat"]
labels = ["KARATE"]

client = pymongo.MongoClient(MONGODB_CONNECTION)
db = client["historical_price_data"]


df = pd.DataFrame(columns=['time'])
df.set_index('time', inplace=True)
for index, coin in enumerate(coinIds):
    col = db[coin]
    cursor = col.find({}, {"_id": 0, "time": 1, "eth_value": 1})
    li = list(cursor)
    df1 = pd.DataFrame(li)
    df1['time'] = pd.to_datetime(df1['time'], unit='ms')
    df1.rename(columns={"eth_value": coin}, inplace=True)
    df1.set_index('time', inplace=True)
    df1.sort_index(inplace=True)
    df = pd.merge(df, df1, on='time', how='outer')

df.sort_index(inplace=True)

def display_bit2_portfolio():
    return html.Div([
        dcc.Graph(
            id="bit2_portfolio_fig", 
            config={"displayModeBar": False},
            style={'height': 700}
        ),
    ])

@app.callback(
    Output("bit2_portfolio_fig", "figure"),
    Input("bit2_portfolio_fig", "relayoutData"),
)
def update_chart(rng):
    traces = []
    end_date = dt.datetime.now()
    start_date = df.index.min()  # Set start_date to the first available date in the DataFrame

    # Check if there's at least a year's worth of data
    one_year_ago = end_date - dt.timedelta(days=365)
    if start_date < one_year_ago:
        start_date = one_year_ago

    if rng and "xaxis.range[0]" in rng.keys():
        start_date = pd.to_datetime(rng.get("xaxis.range[0]"))
        end_date = pd.to_datetime(rng.get("xaxis.range[1]"))

    mask = (df.index >= start_date) & (df.index <= end_date)
    filtered_data = df.loc[mask]

    for index, col in enumerate(filtered_data):
        series = filtered_data[col]
        first = series.index.get_loc(series.first_valid_index())
        reference_value = series[first]
        indexed_series = series.div(reference_value) * 100 - 100
        traces.append(go.Scatter(x=indexed_series.index, y=indexed_series, name=labels[index]))

    layout = dict(
        title=dict(
            text="BIT2 Portfolio (ETH Indexed)",
            x=0.01,
            xanchor="left",
        ),
        margin=dict(l=20,r=100,t=120,b=60,pad=4),
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
            title="",
            range=[start_date, end_date]
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
        ],
        font=dict( 
            size=20
        )
    )

    fig = dict(data=traces, layout=layout)
    return fig
