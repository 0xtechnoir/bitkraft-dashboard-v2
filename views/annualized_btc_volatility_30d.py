from dash import dcc, html
import yfinance as yf
from maindash import app
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import numpy as np
import plotly.graph_objs as go
from pprint import pprint

'''
Volatility is defined as the standard deviation of the last 30 days daily percentage change in BTC price. 
Numbers are annualized by multiplying by the square root of 365, as BTC trades all year round
'''
dxy = yf.Ticker("BTC-USD")
hist = dxy.history(period="max")
btc_data = hist.filter(regex="Close")

# Calculate daily percentage change in BTC price
btc_data["daily_pct_change"] = btc_data["Close"].pct_change()

# Calculate rolling 30-day standard deviation
btc_data["rolling_std"] = btc_data["daily_pct_change"].rolling(window=30).std()

# Annualize the volatility
btc_data["annualized_volatility"] = btc_data["rolling_std"] * np.sqrt(365)

def display_btc_annualized_volatility_30d():
    return html.Div(
        children=dcc.Graph(
            id="btc_annualized_volatility_30d_fig", config={"displayModeBar": False}
        ),
    )

@app.callback(
    Output("btc_annualized_volatility_30d_fig", "figure"),
    Input("btc_annualized_volatility_30d_fig", "relayoutData"),
)
def update_chart(relayoutData):

    fig = px.line(btc_data, x=btc_data.index, y=btc_data["annualized_volatility"])

    if relayoutData is not None and 'xaxis.range[0]' in relayoutData:
        start_date = relayoutData['xaxis.range[0]']
        end_date = relayoutData['xaxis.range[1]']

        fig.update_xaxes(range=[start_date, end_date])
        
        # Filter the data based on the new x-axis range
        mask = (btc_data.index >= start_date) & (btc_data.index <= end_date)
        filtered_data = btc_data[mask]

        # Find the min and max y values within the new x-axis range
        min_y = filtered_data['annualized_volatility'].min()
        max_y = filtered_data['annualized_volatility'].max()

        # Update the y-axis range
        fig.update_yaxes(range=[min_y, max_y])


    fig.update_layout(
        title= dict(
            text="Annualized BTC Volatility (30D)",
            x=0.08,
            xanchor="left"
        ),
        colorway=["#17B897"],
        plot_bgcolor="white",
        yaxis=dict(
            tickformat=".0%", 
            fixedrange= True,
            side="left",
            showline=True,
            linecolor="grey",
            title="",
            showgrid=True,
            gridcolor="lightgrey"
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
                    dict(count=5,
                        label="5y",
                        step="year",
                        stepmode="backward"),
                    dict(step="all")
                ])
            ),
            type="date",
            showline=True,
            linecolor="grey",
            title=""
        )
    )
    
    return fig