from maindash import app
from dash.dependencies import Input, Output
from dash import dcc
from dash import html
import pandas as pd
import pymongo
import plotly.express as px
import os
from dotenv import load_dotenv
from pprint import pprint

load_dotenv()
MONGODB_CONNECTION = os.getenv('MONGODB_CONNECTION')

client = pymongo.MongoClient(MONGODB_CONNECTION)
db = client["historical_price_data"]
col = db["usd_liquidity_conditions_index"]
response = col.find({}, {"_id":0, "date":1, "liquidity_index":1}).sort('date')
df = pd.DataFrame(response)
df.set_index('date', inplace=True)

def display_fed_liquidity_index_chart():
    return html.Div(
        children=dcc.Graph(
            id="fed_liquidity_index_chart", config={"displayModeBar": False}
        ),
    )

@app.callback(
    Output("fed_liquidity_index_chart", "figure"),
    Input("fed_liquidity_index_chart", "relayoutData"),
)
def update_chart(relayoutData=None):

    fig = px.line(df, x=df.index, y=df['liquidity_index'])
    
    if relayoutData is not None and 'xaxis.range[0]' in relayoutData:
        start_date = relayoutData['xaxis.range[0]']
        end_date = relayoutData['xaxis.range[1]']

        fig.update_xaxes(range=[start_date, end_date])
        
        # Filter the data based on the new x-axis range
        mask = (df.index >= start_date) & (df.index <= end_date)
        filtered_data = df[mask]

        # Find the min and max y values within the new x-axis range
        min_y = filtered_data['liquidity_index'].min()
        max_y = filtered_data['liquidity_index'].max()

        # Update the y-axis range
        fig.update_yaxes(range=[min_y, max_y])

    fig.update_layout(
        title= dict(
            text="Fed Liquidity Index",
            x=0.08,
            xanchor="left"
        ),
        colorway=["#17B897"],
        plot_bgcolor="white",
        yaxis=dict(
            tickformat=",.0f", 
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
                    dict(count=2,
                        label="2y",
                        step="year",
                        stepmode="backward"),
                    dict(count=3,
                        label="3y",
                        step="year",
                        stepmode="backward"),
                    dict(count=5,
                        label="5y",
                        step="year",
                        stepmode="backward"),
                    dict(count=10,
                        label="10y",
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