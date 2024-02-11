from dash import dcc
from dash import html
import yfinance as yf
from maindash import app
from dash.dependencies import Input, Output
import plotly.express as px

dxy = yf.Ticker("ETH-USD")
hist = dxy.history(period="max")
df = hist.filter(regex="Close")

def display_eth():
    return html.Div(
        children=dcc.Graph(
            id="eth_fig", config={"displayModeBar": False}
        ),
    )

@app.callback(
    Output("eth_fig", "figure"),
    Input("eth_fig", "relayoutData"),
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

    fig = px.line(df, x=filtered_data.index, y=filtered_data["Close"])

    fig.update_layout(
        title= dict(
            text="ETH",
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
        ),
        font=dict( 
            size=20
        )
    )

    return fig