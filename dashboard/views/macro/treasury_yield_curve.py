from dash import dcc, html
import pandas as pd
import pymongo
import plotly.graph_objs as go
import os
from dotenv import load_dotenv

# Load environment variables and connect to MongoDB
load_dotenv()
MONGODB_CONNECTION = os.getenv('MONGODB_CONNECTION')

def generate_series(data, interval):
    rec = data[interval]
    return [
        rec["bc_1month"],
        rec["bc_2month"],
        rec["bc_3month"],
        rec["bc_6month"],
        rec["bc_1year"],
        rec["bc_2year"],
        rec["bc_3year"],
        rec["bc_5year"],
        rec["bc_7year"],
        rec["bc_10year"],
        rec["bc_20year"],
        rec["bc_30year"]
    ]

client = pymongo.MongoClient(MONGODB_CONNECTION)
db = client["historical_price_data"]
col = db["treasury_yield_curves"]

x = col.find().sort("timestamp", -1)

weekdays_in_1_year = 260
weekdays_in_1_month = round(weekdays_in_1_year / 12)
weekdays_in_6_month = round(weekdays_in_1_year / 2)

d = {
    "Residual Maturity" : ["1M", "2M", "3M", "5M", "1Y", "2Y", "3Y", "5Y", "7Y", "10Y", "20Y", "30Y"],
    "Latest" : generate_series(x, 0),
    "-1W": generate_series(x, 5),
    "-1M": generate_series(x, weekdays_in_1_month),
    "-6M": generate_series(x, weekdays_in_6_month),
    "-1Y": generate_series(x, weekdays_in_1_year)
}

df = pd.DataFrame(d)

def display_treasury_yield_curve():
    
    color_map = {
        "-1W": "#FADBD8",
        "-1M": "#EBDEF0",
        "-6M": "#D4E6F1",
        "-1Y": "#D4EFDF",
        "Latest": "#2ECC71",
    }

    # Create traces for each series
    traces = [
        go.Scatter(
            x=df['Residual Maturity'], 
            y=df[col], 
            mode='lines', 
            name=col,
            line_shape='spline',
            line=dict(color=color_map[col])
        ) for col in ["Latest", "-1W", "-1M", "-6M", "-1Y"]
    ]

    layout = dict(
        title=dict(
            text="Treasury Yield Curve",
            x=0.02,
            xanchor="left",
        ),
        plot_bgcolor="white",
        margin=dict(l=60,r=20,t=80,b=20,pad=4),
        yaxis=dict(
            tickformat=".1f", 
            fixedrange=True,
            side="left",
            ticksuffix="%",
            showline=True,
            linecolor="grey",
            title=""
        ),
        xaxis=dict( 
            fixedrange=True,
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
        )
    )
    
    fig = dict(data=traces, layout=layout)
    return html.Div([
        dcc.Graph(figure=fig, 
                  config={"displayModeBar": False}),
    ])