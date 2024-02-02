import requests
import pandas as pd
from dash import dcc
from dash import html
from maindash import app
from dash.dependencies import Input, Output
import plotly.express as px

response = requests.get("https://api.alternative.me/fng/?limit=0")
data = response.json()
df = pd.DataFrame(data['data'])
df.drop('time_until_update', axis=1, inplace=True)
df = df.sort_values('timestamp', ascending=True)
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
df.set_index('timestamp', inplace=True)
df['value'] = df['value'].astype(int)

def display_fear_and_greed_chart():
    return html.Div(
        children=dcc.Graph(
            id="fear_and_greed_fig", config={"displayModeBar": False}
        ),
    )

@app.callback(
    Output("fear_and_greed_fig", "figure"),
    Input("fear_and_greed_fig", "relayoutData"),
)
def update_chart(relayoutData=None):

    fig = px.line(df, x=df.index, y=df['value'])
    
    if relayoutData is not None and 'xaxis.range[0]' in relayoutData:
        start_date = relayoutData['xaxis.range[0]']
        end_date = relayoutData['xaxis.range[1]']

        fig.update_xaxes(range=[start_date, end_date])

    fig.update_layout(
        title= dict(
            text="Fear & Greed Index",
            x=0.08,
            xanchor="left"
        ),
        margin=dict(l=20,r=100,t=120,b=60,pad=4),
        colorway=["#17B897"],
        plot_bgcolor="white",
        height=600,
        yaxis=dict(
            tickformat=".0f", 
            fixedrange= True,
            side="right",
            showline=True,
            linecolor="grey",
            title="",
            showgrid=False,
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
        ),
        font=dict( 
            size=20
        )
    )
    
    return fig