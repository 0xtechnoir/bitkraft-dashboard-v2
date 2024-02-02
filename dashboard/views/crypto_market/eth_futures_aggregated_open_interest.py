from maindash import app
import pandas as pd
from dash import html, dcc
import pymongo
import pandas as pd
from dash.dependencies import Input, Output
import plotly.express as px
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()
MONGODB_CONNECTION = os.getenv('MONGODB_CONNECTION')
client = pymongo.MongoClient(MONGODB_CONNECTION)
db = client["historical_price_data"]
eth_collection = db.eth_aggregated_open_interest

min_date = datetime(2022, 7, 12)
min_date_timestamp = int(min_date.timestamp())
data = list(eth_collection.find({"timestamp": {"$gte": min_date_timestamp}}, {'_id': 0}))

df = pd.DataFrame.from_dict(data).set_index("timestamp")
df = df.exchanges_agg.apply(pd.Series).reset_index()

# Convert the DataFrame to a long format
df = df.melt(id_vars="timestamp", var_name="exchange", value_name="open_interest")

# Convert the 'timestamp' column to datetime format
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')

# Sort the DataFrame by 'timestamp' in ascending order
df = df.sort_values(by='timestamp', ascending=True)
df_pivoted = df.pivot(index='timestamp', columns='exchange', values='open_interest')

def display_eth_futures_agg_open_interest_chart():
    return html.Div(
        children=dcc.Graph(
            id="eth_agg_open_interest_fig", 
            figure=update_chart(),
            config={"displayModeBar": False}
        ),
    )

@app.callback(
    Output('eth_agg_open_interest_fig', 'figure'),
    Input("eth_agg_open_interest_fig", "relayoutData"),
)
def update_chart(relayoutData=None):
   
    fig = px.area(df, x='timestamp', y='open_interest', color='exchange', 
                  line_shape='linear')
    
    if relayoutData is not None and 'xaxis.range[0]' in relayoutData:
        start_date = relayoutData['xaxis.range[0]']
        end_date = relayoutData['xaxis.range[1]']

        fig.update_xaxes(range=[start_date, end_date])
        
        # Filter the data based on the new x-axis range
        mask = (df['timestamp'] >= start_date) & (df['timestamp'] <= end_date)
        filtered_data = df[mask]

        # Group the data by timestamp and sum the open_interest values across all exchanges
        grouped_data = filtered_data.groupby('timestamp')['open_interest'].sum()

        # Find the min and max y values within the new x-axis range
        min_y = 0
        max_y = grouped_data.max()

        # Update the y-axis range and tick labels
        tickvals = list(range(int(min_y), int(max_y) + 1, int((max_y - min_y) / 5)))
        ticktext = [f"${x / 1_000_000_000:.1f}B" for x in tickvals]
        fig.update_yaxes(range=[min_y, max_y], tickvals=tickvals, ticktext=ticktext)

    fig.update_layout(
        title=dict(
            text="ETH Futures Aggregated Open Interest",
            x=0.08,
            xanchor="left",
        ),
        colorway=["#17B897"],
        plot_bgcolor="white",
        margin=dict(l=20,r=100,t=120,b=20,pad=4),
        height=600,
        yaxis=dict(
            fixedrange= True,
            side="right",
            showline=True,
            linecolor="grey",
            title=""
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.3,
            xanchor="center",
            x=0.5,
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
            title="",
            dtick="M12",
        ),
        font=dict( 
            size=20
        )
    )
    
    return fig

