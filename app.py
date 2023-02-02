from dash import html
from maindash import app
from views.header import display_header
from views.treasury_yield_curve import display_treasury_yield_curve
from maindash import data
import dash_bootstrap_components as dbc
from views.dxy import display_dxy
from views.brent import display_brent
from views.gold import display_gold
from views.ftse100 import display_ftse
from views.sp500 import display_sp500
from views.nasaq import display_nasdaq
from views.hangseng import display_hangseng
from views.gaming_equities import display_gaming_equities

server = app.server

app.layout = html.Div(
        [
            display_header(),
            dbc.Row(
                [
                    dbc.Col(display_treasury_yield_curve(), width=6),
                    dbc.Col(display_dxy(), width=6),
                ],
            ),
            dbc.Row(
                [
                    dbc.Col(display_brent(), width=6),
                    dbc.Col(display_gold(), width=6),
                ],
            ),
            dbc.Row(
                [
                    dbc.Col(display_ftse(), width=6),
                    dbc.Col(display_sp500(), width=6),
                ],
            ),
            dbc.Row(
                [
                    dbc.Col(display_nasdaq(), width=6),
                    dbc.Col(display_hangseng(), width=6),
                ],
            ),
            dbc.Row(
                [
                    dbc.Col(display_gaming_equities(), width=6),
                ],
            )
        ]
    )


    
if __name__ == "__main__":
    app.run_server(debug=True)