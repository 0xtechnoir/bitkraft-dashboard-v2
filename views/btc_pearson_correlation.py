from maindash import app
from dash import dcc, html
from dash.dependencies import Input, Output
import yfinance as yf
from datetime import datetime
import plotly.express as px

# Gold, Nasdaq Composit, S&P500, BTC
tickers = ["GC=F", "^IXIC", "^GSPC", "BTC-USD"]

df = yf.download(
    tickers, 
    start="2015-01-01", 
    end=datetime.now(), 
    interval="1d",
)

df = df.filter(regex="Adj Close")
df = df.dropna()
df = df["Adj Close"]
df = df.rename(columns={'GC=F': 'Gold', '^IXIC':'Nasdaq Composite', '^GSPC': 'S&P500', 'BTC-USD': 'BTC'})

# calculate correlations
df['BTC-Gold'] = df['BTC'].rolling(30).corr(df['Gold'])
df['BTC-Nasdaq'] = df['BTC'].rolling(30).corr(df['Nasdaq Composite'])
df['BTC-SP500'] = df['BTC'].rolling(30).corr(df['S&P500'])

def display_btc_pearson_correlation():
    return html.Div(
        children=dcc.Graph(
            id="correlation_fig", 
            figure=update_chart(),
            config={"displayModeBar": False}
        ),
    )

# @app.callback(
#     Output('correlation_fig', 'figure'),
#     [Input(component_id='_dummy-input', component_property='children')]
# )
def update_chart():
   
    fig = px.line(df, x=df.index, y=['BTC-Gold', 'BTC-Nasdaq', 'BTC-SP500'])

    fig.update_layout(
        title=dict(
            text="BTC Pearson Correlation 30D",
            x=0.08,
            xanchor="left",
        ),
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
    
    return fig