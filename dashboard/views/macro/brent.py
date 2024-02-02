from pandas import Timestamp
from datetime import datetime, timedelta
from dash import dcc
from dash import html
import yfinance as yf
from maindash import app
from dash.dependencies import Input, Output
import plotly.graph_objs as go

dxy = yf.Ticker("BZ=F")
hist = dxy.history(period="max")
df = hist.filter(regex="Close")

def display_brent():
    return html.Div(
        children=dcc.Graph(
            id="oil_fig", config={"displayModeBar": False}
        ),
    )

@app.callback(
    Output("oil_fig", "figure"),
    Input("oil_fig", "relayoutData"),
)
def update_chart(rng):

    filtered_data = df
    # Check if DataFrame's index is timezone-aware and get its timezone
    tz = df.index.tz if df.index.tz is not None else 'UTC'
    end_date = Timestamp(datetime.now(), tz=tz)
    start_date = end_date - timedelta(days=5 * 365)

    # If there's a range selection from user, update the start and end dates
    if rng and "xaxis.range[0]" in rng.keys():
        start_date = Timestamp(rng.get("xaxis.range[0]"), tz=tz)
        end_date = Timestamp(rng.get("xaxis.range[1]"), tz=tz)

    # Filter the data based on the calculated range
    mask = (df.index >= start_date) & (df.index <= end_date)
    filtered_data = df.loc[mask]
    
    # Calculate min and max values for y-axis
    y_min = filtered_data["Close"].min()
    y_max = filtered_data["Close"].max()

    trace = go.Scatter(x= filtered_data.index, y=filtered_data["Close"], mode='lines')

    layout = dict(
        title= dict(
            text="Brent Crude Oil",
            x=0.05,
            xanchor="left"
        ),
        colorway=["#17B897"],
        plot_bgcolor="white",
        # margin=dict(l=40,r=80,t=120,b=60,pad=4),
        margin=dict(l=20,r=100,t=120,b=60,pad=4),
        height=500,
        yaxis=dict(
            tickformat=".0f", 
            fixedrange= True,
            side="right",
            showline=True,
            linecolor="grey",
            title="",
            range=[y_min, y_max]
        ),
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(count=5, label="5y", step="year", stepmode="backward"),
                    dict(step="all")
                ])
            ),
            range=[start_date, end_date],
            type="date",
            showline=True,
            linecolor="grey",
            title=""
        ),
        font=dict( 
            size=20
        )
    )
    fig = dict(data=[trace], layout=layout)

    return fig