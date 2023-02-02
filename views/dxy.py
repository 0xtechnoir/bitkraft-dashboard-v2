from dash import dcc
from dash import html
import yfinance as yf
import plotly.express as px
from maindash import app
from dash.dependencies import Input, Output

dxy = yf.Ticker("DX-Y.NYB")
hist = dxy.history(period="max")

def display_dxy():
    return html.Div(
        children=dcc.Graph(
            id="dxy_fig", 
            config={"displayModeBar": False},
            figure={
                "layout": {
                    "title": "US Dollar Index (DXY)",
                }
            }           
        ),
    )

@app.callback(
    Output("dxy_fig", "figure"),
    Input("dxy_fig", "relayoutData"), 
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
        title="DXY",
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