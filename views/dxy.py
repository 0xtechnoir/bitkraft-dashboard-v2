from dash import dcc
from dash import html
import yfinance as yf
import plotly.express as px
import pandas_datareader.data as web
import plotly.graph_objs as go
from datetime import datetime
from dateutil.relativedelta import relativedelta
from maindash import app
from dash.dependencies import Input, Output

dxy = yf.Ticker("DX-Y.NYB")
hist = dxy.history(period="max")

# def zoom(layout, xrange):
#     in_view = df.loc[fig.layout.xaxis.range[0]:fig.layout.xaxis.range[1]]
#     fig.layout.yaxis.range = [in_view.High.min() - 10, in_view.High.max() + 10]

# trace = go.Line(x=list(hist.index),
#                     y=list(hist.Close))

# data = [trace]

# layout = dict(
#     title='Time series with range slider and selectors',
#     xaxis=dict(
#         rangeselector=dict(
#             buttons=list([
#                 dict(count=1,
#                     label='1m',
#                     step='month',
#                     stepmode='backward'),
#                 dict(count=6,
#                     label='6m',
#                     step='month',
#                     stepmode='backward'),
#                 dict(count=1,
#                     label='YTD',
#                     step='year',
#                     stepmode='todate'),
#                 dict(count=1,
#                     label='1y',
#                     step='year',
#                     stepmode='backward'),
#                 dict(step='all')
#             ])
#         ),
#         rangeslider=dict(
#             visible = True
#         ),
#         type='date'
#     )
# )
# fig = go.FigureWidget(data=data, layout=layout)
# fig.layout.on_change(zoom, 'xaxis.range')

# def display_dxy():
#     return html.Div([
#         dcc.Graph(figure=fig, config={"displayModeBar": False}),
#     ])

now = datetime.now()
yearago = now - relativedelta(years=1)
fig = px.line(hist, x=hist.index, y="Close")
fig.layout = {
    "title": {"text": "US Dollar Index (DXY)", "x": 0.08, "xanchor": "left"},
}
fig.update_yaxes(fixedrange=False)
fig.update_xaxes(fixedrange=False)
fig.update_xaxes(range = [yearago, now])
# Add range slider
# fig.update_layout(
#     xaxis=dict(
#         autorange=False,
#         rangeselector=dict(
#             buttons=list([
#                 dict(count=1,
#                     label="1m",
#                     step="month",
#                     stepmode="backward"),
#                 dict(count=6,
#                     label="6m",
#                     step="month",
#                     stepmode="backward"),
#                 dict(count=1,
#                     label="YTD",
#                     step="year",
#                     stepmode="todate"),
#                 dict(count=1,
#                     label="1y",
#                     step="year",
#                     stepmode="backward"),
#                 dict(step="all")
#             ])
#         ),
#         type="date"
#     )
# )

def display_dxy():
    return html.Div(
        children=dcc.Graph(
            id="fig", config={"displayModeBar": False}
        ),
    )

@app.callback(
    Output("fig", "figure"),
    Input("fig", "relayoutData"),
)
def update_chart(rng):

    filtered_data = hist

    if rng and "xaxis.range[0]" in rng.keys():
        print("keys:", list(rng.keys())[0])
        print("keys:", rng.get(list(rng.keys())[0]))

        lower = rng.get(list(rng.keys())[0])
        upper = rng.get(list(rng.keys())[1])

        mask = ((hist.index >= lower)
                & (hist.index <= upper)
            )
        filtered_data = hist.loc[mask, :]
    
    fig = {
        "data": [
            {
                "x": filtered_data.index,
                "y": filtered_data["Close"],
                "type": "lines",
            },
        ],
        "layout": {
            "title": {
                "text": "DXY",
                "x": 0.05,
                "xanchor": "left",
            },
            "xaxis": {
                "fixedrange": True,
                "rangeselector": {
                    "buttons": [
                        {
                            "count": 1,
                            "label": "1m",
                            "step": "month",
                            "stepmode": "backward",
                        },
                        {
                            "count": 6,
                            "label": "6m",
                            "step": "month",
                            "stepmode": "backward",
                        },
                        {
                            "count": 1,
                            "label": "YTD",
                            "step": "year",
                            "stepmode": "todate",
                        },
                        {
                            "count": 1,
                            "label": "1y",
                            "step": "year",
                            "stepmode": "backward",
                        },
                        {
                            "step": "all",
                        }
                    ]
                }
            
            },
            "yaxis": {"tickprefix": "$", "fixedrange": True},
            "colorway": ["#17B897"],  
        }
    }
    return fig


# def scaleYaxis(rng):
#     # and "xaxis.range" in rng.keys()
#     print("1 =================================")
#     print("rng items (before): ", rng.items())

#     if rng and "xaxis.range[0]" in rng.keys():
#         print("keys:", list(rng.keys())[0])
#         print("keys:", rng.get(list(rng.keys())[0]))

#         lower = rng.get(list(rng.keys())[0])
#         upper = rng.get(list(rng.keys())[1])
#         print("lower: ", lower)
#         print("upper: ", upper)
#         try:
#             d = hist.loc[
#                 lower : upper,
#                 ["High", "Low", "Open", "Close"],
#             ]
#             if len(d) > 0:
#                 print("2")
#                 # fig["layout"]["yaxis"]["range"] = [d.min().min(), d.max().max()]
#                 fig.update_yaxes(range = [d.min().min(), d.max().max()])
#                 fig.update_xaxes(range = [lower, upper])
#                 print("y range: ", fig["layout"]["yaxis"]["range"])
#                 print("3")
#         except KeyError:
#             print("4")
#             pass
#         finally:
#             print("5")
#             print("x range: ", fig["layout"]["xaxis"]["range"])
#             # print("range: ", dir(rng))
#             print("rng items (after): ", rng.items())
#             # print("fig dir: ", dir(fig))
#             # fig["layout"]["xaxis"]["range"] = rng["xaxis.range"]
            
#             print("6")

#     return fig
    