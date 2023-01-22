from dash import html
from maindash import app
from views.header import display_header
from views.treasury_yield_curve import display_treasury_yield_curve
from maindash import data
import dash_bootstrap_components as dbc
from views.dxy import display_dxy

server = app.server

app.layout = html.Div(
        [
            display_header(),
            dbc.Row(
                [
                    dbc.Col(display_treasury_yield_curve(), width=6),
                    dbc.Col(display_dxy(), width=6),
                ],
            )
        ]
    )


    
if __name__ == "__main__":
    app.run_server(debug=True)