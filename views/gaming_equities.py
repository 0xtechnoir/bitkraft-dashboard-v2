from dash import dcc
from dash import html
import yfinance as yf
import plotly.express as px
from datetime import datetime
from maindash import app
from dash.dependencies import Input, Output

tickers = ["^GSPC", "NERD", "GAMR", "HERO", "ESPO"]

df = yf.download(
    tickers, 
    start="2019-05-15", 
    end=datetime.now(), 
    interval="1d",
)

df = df.filter(regex="Adj Close")
df = df.dropna()
df = df["Adj Close"]
df = df.rename(columns={'^GSPC': 'S&P500'})

def display_gaming_equities():
    return html.Div(
        children=dcc.Graph(
            id="gaming_equities_fig", 
            config={"displayModeBar": False},
        ),
    )

@app.callback(
    Output("gaming_equities_fig", "figure"),
    Input("gaming_equities_fig", "relayoutData"),
)
def update_chart(rng):

    if rng and "xaxis.range[0]" in rng.keys():

        lower = rng.get(list(rng.keys())[0])
        upper = rng.get(list(rng.keys())[1])

        range = ((df.index >= lower)
                & (df.index <= upper)
            )
        
        filtered_df = df.loc[range, :]       
        reference_value = filtered_df.iloc[0]        
        indexed_df = filtered_df.div(reference_value) * 100 - 100        
        fig = px.line(indexed_df, x=indexed_df.index, y=indexed_df.columns)

    else:
        reference_value = df.iloc[0]
        indexed_df = df.div(reference_value) * 100 - 100
        fig = px.line(indexed_df, x=indexed_df.index, y=indexed_df.columns)
    
    fig.update_layout(
        title=dict(
            text="Gaming Equities",
            x=0.08,
            xanchor="left",
        ),
        colorway=["#17B897"],
        plot_bgcolor="white",
        yaxis=dict(
            tickformat=".2f", 
            fixedrange= True,
            side="right",
            ticksuffix="%",
            showline=True,
            linecolor="grey",
            title=""
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
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
        )
    )

    fig.add_hline(y=0, line_dash="dash", line_color="black", line_width=0.5, opacity=0.7)

    return fig