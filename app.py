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
from views.bit1_portfolio import display_bit1_portfolio
from views.btc import display_btc
from views.eth import display_eth
from views.crypto_price_performance_30d import display_crypto_price_performance_30d_chart
from views.bit1_token_performance_table_usd import display_bit1_portfolio_table_usd
from views.bit1_token_performance_table_eth import display_bit1_portfolio_table_eth

server = app.server

app.layout = html.Div(
        [
            display_header(),
            dbc.Row(
                [
                    dbc.Col(display_treasury_yield_curve(), width=4),
                    dbc.Col(display_dxy(), width=4),
                    dbc.Col(display_brent(), width=4)
                ],
            ),
            dbc.Row(
                [
                    dbc.Col(display_gold(), width=4),
                    dbc.Col(display_ftse(), width=4),
                    dbc.Col(display_sp500(), width=4),
                ],
            ),
            dbc.Row(
                [
                    dbc.Col(display_nasdaq(), width=4),
                    dbc.Col(display_hangseng(), width=4),
                    
                ],
            ),
            dbc.Row(
                [
                    dbc.Col(display_gaming_equities(), width=8),
                ],
            ),
            dbc.Row(
                [
                    dbc.Col(display_bit1_portfolio(), width=8),
                ],
            ),
            dbc.Row(
                [
                    dbc.Col(display_bit1_portfolio_table_usd(), width=8),
                ],
            ),
            dbc.Row(
                [                 
                    dbc.Col(display_crypto_price_performance_30d_chart(), width=8),
                ],
            ),
            dbc.Row(
                [                 
                    dbc.Col(display_btc(), width=4),
                    dbc.Col(display_eth(), width=4),
                ],
            ),
        ]
    )


    
if __name__ == "__main__":
    app.run_server(debug=True)