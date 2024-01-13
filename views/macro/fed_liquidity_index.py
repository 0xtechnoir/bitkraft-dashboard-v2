from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import pymongo
import os
from maindash import app
from dotenv import load_dotenv
import plotly.graph_objs as go
from pandas import Timestamp
from datetime import datetime, timedelta

# Load environment variables and connect to MongoDB
load_dotenv()
MONGODB_CONNECTION = os.getenv('MONGODB_CONNECTION')
client = pymongo.MongoClient(MONGODB_CONNECTION)
db = client["historical_price_data"]
col = db["usd_liquidity_conditions_index"]

# Fetch and prepare data
response = col.find({}, {"_id":0, "date":1, "liquidity_index":1}).sort('date')
df = pd.DataFrame(response)
df.set_index('date', inplace=True)

# Display function
def display_fed_liquidity_index_chart():
    return html.Div(
        children=dcc.Graph(
            id="fed_liquidity_index_chart", 
            config={"displayModeBar": False}
        ),
    )

# Callback for updating the chart
@app.callback(
    Output("fed_liquidity_index_chart", "figure"),
    Input("fed_liquidity_index_chart", "relayoutData"),
)
def update_chart(relayoutData=None):
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=5 * 365)

    # If there's a range selection from user, update the start and end dates
    if relayoutData and "xaxis.range[0]" in relayoutData:
        start_date = pd.to_datetime(relayoutData["xaxis.range[0]"])
        end_date = pd.to_datetime(relayoutData["xaxis.range[1]"])

    # Convert start_date and end_date to string format for comparison
    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")

    # Filter the data based on the calculated range
    mask = (df.index >= start_date_str) & (df.index <= end_date_str)
    filtered_data = df.loc[mask]

    # Create the trace for the line chart
    trace = go.Scatter(x=filtered_data.index, y=filtered_data['liquidity_index'], mode='lines')

    # Create the layout for the chart
    layout = dict(
        title=dict(
            text="Fed Liquidity Index",
            x=0.03,
            xanchor="left"
        ),
        colorway=["#17B897"],
        plot_bgcolor="white",
        margin=dict(l=20, r=50, t=80, b=20, pad=4),
        yaxis=dict(
            tickformat=".2s",
            fixedrange=True,
            side="right",
            showline=True,
            linecolor="grey",
            title="",
        ),
        xaxis=dict(
            rangeselector=dict(
                buttons=[
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(count=2, label="2y", step="year", stepmode="backward"),
                    dict(count=3, label="3y", step="year", stepmode="backward"),
                    dict(count=5, label="5y", step="year", stepmode="backward"),
                    dict(count=10, label="10y", step="year", stepmode="backward"),
                    dict(step="all")
                ]
            ),
            range=[start_date, end_date],
            type="date",
            showline=True,
            linecolor="grey",
            title="",
        )
    )

    fig = dict(data=[trace], layout=layout)
    return fig
