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

coinIds = ["ethereum", "bitcoin", "defipulse-index"]
labels = ["ETH", "BTC", "DPI"]

client = pymongo.MongoClient(MONGODB_CONNECTION)
db = client["historical_price_data"]

# Create an empty dataframe
df = pd.DataFrame(columns=['time'])
df.set_index('time', inplace=True)

# Loop through the coinIds and create a dataframe for each coin
for index, coin in enumerate(coinIds):
    col = db[coinIds[index]]
    cursor = col.find({}, {"_id":0, "time":1, "usd_value":1})
    # Convert the cursor to a list of dictionaries, then to a dataframe
    li = list(cursor)
    df1 = pd.DataFrame(li)
    # Convert the time column to datetime type
    df1['time'] = pd.to_datetime(df1["time"], unit="ms")
    coin_name = (coinIds[index])
    df1.rename(columns={"usd_value":coin_name}, inplace = True)
    # Set the time column as the index and sort the dataframe
    df1.set_index('time', inplace=True)
    df1.sort_index(inplace=True)
    # Merge each coins dataframe with the empty dataframe
    df = pd.merge(df, df1, on='time', how='outer')

# Sort the finished dataframe by time
df.sort_index(inplace=True)   

def display_crypto_price_performance_30d_chart():
    return html.Div(
        children=dcc.Graph(
            id="crypto_price_performance_fig", 
            config={"displayModeBar": False},
        ),
    )

@app.callback(
    Output("crypto_price_performance_fig", "figure"),
    Input("crypto_price_performance_fig", "relayoutData"),
)
def update_chart(update):

    fig = go.Figure()
    if update and "xaxis.range[0]" in update.keys():
        # If the user has selected a range, then filter the dataframe
        lower = update.get(list(update.keys())[0])
        upper = update.get(list(update.keys())[1])
        range = ((df.index >= lower) & (df.index  <= upper))
        filtered_df = df.loc[range, :]
        
        # Loop through each column of the filtered dataframe
        for index, col in enumerate(filtered_df):
            series = filtered_df[col]
            # first valid position, i.e. first non-NaN value and use it to reference value for the indexed series
            reference_value = series[0]
            indexed_series = series.div(reference_value) * 100 - 100  
            fig.add_trace(go.Scatter(x=indexed_series.index, y=indexed_series, name=labels[index]))

    else:
        # If the user has not selected a range, then use the full dataframe
        for index, col in enumerate(df):
            series = df[col]
            # first valid position, i.e. first non-NaN value and use it to reference value for the indexed series
            first = series.index.get_loc(series.first_valid_index())
            reference_value = series[first]
            indexed_series = series.div(reference_value) * 100 - 100  
            fig.add_trace(go.Scatter(x=indexed_series.index, y=indexed_series, name=labels[index]))
        
    fig.update_layout(
        title=dict(
                text="Crypto Price Performance",
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