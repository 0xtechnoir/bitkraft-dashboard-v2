from dash import dcc
from dash import html
import pandas as pd
import pymongo
import plotly.express as px

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

client = pymongo.MongoClient("mongodb+srv://bkCryptoTeam:Dg7PLzRxUwFa6Yvr@cluster0.tmpq7.mongodb.net/?retryWrites=true&w=majority")
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
    
    fig = px.line(df, x="Residual Maturity", y=["Latest", "-1W", "-1M", "-6M", "-1Y"])
    
    fig.update_layout(
        title=dict(
            text="Treasury Yield Curve",
            x=0.08,
            xanchor="left",
        ),
        plot_bgcolor="white",
        yaxis=dict(
            tickformat=".2f", 
            fixedrange= True,
            side="left",
            ticksuffix="%",
            showline=True,
            linecolor="grey",
            title=""
        ),
        xaxis=dict( 
            fixedrange= True,
            showline=True,
            linecolor="grey",
            title="Residual Maturity"
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
    
    return html.Div([
        dcc.Graph(figure=fig, config={"displayModeBar": False}),
    ])