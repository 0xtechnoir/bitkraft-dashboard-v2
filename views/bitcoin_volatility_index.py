from dash import dcc, html
from maindash import app
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
from pprint import pprint
import requests

'''
The Bitcoin Volatility Index (BVIN) was launched by CryptoCompare and the University of Sussex Business School.

The index measures the implied volatility of bitcoin — the view on volatility over the next 30 days held by bitcoin 
option traders. Other VIX indices are used for settlement prices of volatility futures contracts in traditional markets. 
The index represents a valuable tool for institutional investors to price bitcoin volatility risk, and hedge and trade 
on bitcoin volatility.
'''

url = "https://min-api.cryptocompare.com/data/index/histo/day?indexName=BVIN&limit=2000"

response = requests.get(url)
if response.status_code == 200:
    try:
        print("response.status_code", response.status_code)
        data = response.json()
        print("xxxxxxxxxxdata", data)
        df = pd.DataFrame(data['Data'])
        # Remove any rows containing '0' values
        print("xxxxxxxxxx", df)
        df = df[df.ne(0).all(axis=1)]
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df.set_index('time', inplace=True)
    except:
        print("Error:", response.status_code, response.text)
else:
    print("Error:", response.status_code, response.text)

def display_btc_volatility_index():
    return html.Div(
        children=dcc.Graph(
            id="btc_volatility_index_fig", config={"displayModeBar": False}
        ),
    )

@app.callback(
    Output("btc_volatility_index_fig", "figure"),
    Input("btc_volatility_index_fig", "relayoutData"),
)
def update_chart(relayoutData):

    fig = px.line(df, x=df.index, y=df["close"])

    if relayoutData is not None and 'xaxis.range[0]' in relayoutData:
        start_date = relayoutData['xaxis.range[0]']
        end_date = relayoutData['xaxis.range[1]']

        fig.update_xaxes(range=[start_date, end_date])
        
        # Filter the data based on the new x-axis range
        mask = (df.index >= start_date) & (df.index <= end_date)
        filtered_data = df[mask]

        # Find the min and max y values within the new x-axis range
        min_y = filtered_data['close'].min()
        max_y = filtered_data['close'].max()

        # Update the y-axis range
        fig.update_yaxes(range=[min_y, max_y])


    fig.update_layout(
        title= dict(
            text="BTC Volatility Index (BVIN)",
            x=0.08,
            xanchor="left"
        ),
        colorway=["#17B897"],
        plot_bgcolor="white",
        yaxis=dict(
            tickformat=".0f", 
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