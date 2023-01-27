from dash import dcc
from dash import html
import yfinance as yf
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from datetime import datetime
from dateutil.relativedelta import relativedelta
from maindash import app
from dash.dependencies import Input, Output
from pytz import timezone

dxy = yf.Ticker("^HSI")
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

def display_hangseng():
    return html.Div(
        children=dcc.Graph(
            id="hangseng_fig", config={"displayModeBar": False}
        ),
    )

@app.callback(
    Output("hangseng_fig", "figure"),
    Input("hangseng_fig", "relayoutData"),
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

    data = go.Line(x=filtered_data.index, y=filtered_data["Close"])

    layout = go.Layout(
        title="Hang Seng Index",
        colorway=["#17B897"],
        plot_bgcolor="white",
        # annotations=[
        #     go.layout.Annotation(
        #         x=filtered_data.tail(1).index,
        #         y=filtered_data.tail(1).iloc[0, "Close"],
        #         text=str(y[-1]),
        #         showarrow=True,
        #         arrowhead=7,
        #         ax=0,
        #         ay=-40
        #     )
        # ],
        yaxis=dict(
            tickformat=".1f", 
            fixedrange= True,
            side="right",
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
            type="date"
        )
    )
    fig = go.Figure(data=data, layout=layout)

    return fig