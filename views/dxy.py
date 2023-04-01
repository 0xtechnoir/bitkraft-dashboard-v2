from dash import dcc
from dash import html
import yfinance as yf
from maindash import app
from dash.dependencies import Input, Output
import plotly.express as px
from datetime import datetime, timedelta
import pandas as pd

dxy = yf.Ticker("DX-Y.NYB")
hist = dxy.history(period="max")
df = hist.filter(regex="Close")

now = pd.Timestamp(datetime.now(), tz="America/New_York")
five_years_ago = now - timedelta(days=5 * 365)

def display_dxy():
    return html.Div(
        children=dcc.Graph(
            id="dxy_fig", 
            config={"displayModeBar": False},
        ),
    )

@app.callback(
    Output("dxy_fig", "figure"),
    Input("dxy_fig", "relayoutData"), 
)
def update_chart(rng):

    filtered_data = df
    
    if rng and "xaxis.range[0]" in rng.keys():

        lower = rng.get(list(rng.keys())[0])
        upper = rng.get(list(rng.keys())[1])

        mask = ((df.index >= lower)
                & (df.index <= upper)
            )
        filtered_data = df.loc[mask]
    else:
        lower = five_years_ago
        upper = now
        mask = ((df.index >= lower)
                & (df.index <= upper)
            )
        filtered_data = df.loc[mask]


    fig = px.line(df, x=filtered_data.index, y=filtered_data["Close"])

    y_min = filtered_data['Close'].min()
    y_max = filtered_data['Close'].max()
    
    fig.update_layout(
        title= dict(
            text="US Dollar Index (DXY)",
            x=0.08,
            xanchor="left"
        ),
        colorway=["#17B897"],
        plot_bgcolor="white",
        yaxis=dict(
            tickformat=".1f", 
            fixedrange= True,
            range=[y_min, y_max],
            side="right",
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
                    dict(count=5,
                        label="5y",
                        step="year",
                        stepmode="backward"),
                ])
            ),
            range=[lower, now],
            type="date",
            showline=True,
            linecolor="grey",
            title=""
        )
    )

    return fig