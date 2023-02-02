from dash import dcc
from dash import html
import yfinance as yf
import pandas as pd
import plotly.express as px
from datetime import datetime
from dateutil.relativedelta import relativedelta
from maindash import app
from dash.dependencies import Input, Output
from pytz import timezone

dxy = yf.Ticker("BZ=F")
hist = dxy.history(period="max")

now = pd.to_datetime(datetime.now(), utc=True).tz_convert('America/New_York')
yearago = datetime.now() - relativedelta(years=1)
yearago = pd.to_datetime(yearago, utc=True).tz_convert('America/New_York')

fig = px.line(hist, x=hist.index, y="Close")
fig.layout = {
    "title": {"text": "US Dollar Index (DXY)", "x": 0.08, "xanchor": "left"},
}
fig.update_yaxes(fixedrange=False)
fig.update_xaxes(fixedrange=False)
fig.update_xaxes(range = [yearago, now])

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

    filtered_data = hist

    if rng and "xaxis.range[0]" in rng.keys():

        lower = rng.get(list(rng.keys())[0])
        upper = rng.get(list(rng.keys())[1])

        mask = ((hist.index >= lower)
                & (hist.index <= upper)
            )
        filtered_data = hist.loc[mask, :]

    fig = px.line(filtered_data, x=filtered_data.index, y=filtered_data["Close"])

    fig.update_layout(
        title="Oil",
        colorway=["#17B897"],
        plot_bgcolor="white",
        yaxis=dict(
            tickformat=".1f", 
            fixedrange= True,
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