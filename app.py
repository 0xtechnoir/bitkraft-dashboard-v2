from dash import html
from maindash import app
import requests
import subprocess
from flask import request
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

#  Views - Individual Charts
from views.header import display_header
from views.treasury_yield_curve import display_treasury_yield_curve
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
from views.btc_pearson_correlation import display_btc_pearson_correlation
from views.nft_rankings import display_nft_collection_ranking_table
from views.iframe_test import display_iframe

server = app.server
app.layout = html.Div(
        [
            display_header(),
            dbc.Row(
                [
                    dbc.Col(display_treasury_yield_curve()),
                    dbc.Col(display_dxy()),
                    dbc.Col(display_brent())
                ],
            ),
            dbc.Row(
                [
                    dbc.Col(display_gold()),
                    dbc.Col(display_ftse()),
                    dbc.Col(display_sp500()),
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
                    dbc.Col(display_btc(), width=4),
                ],
            ),
            dbc.Row(
                [
                    dbc.Col(display_bit1_portfolio_table_usd(), width=8),
                ],
            ),
            dbc.Row(
                [                 
                    dbc.Col(display_eth(), width=4),
                    dbc.Col(display_crypto_price_performance_30d_chart(), width=8),
                ],
            ),
            dbc.Row(
                [                 
                    dbc.Col(display_btc_pearson_correlation(), width=8),
                ],
            ),
            dbc.Row(
                [                 
                    dbc.Col(display_nft_collection_ranking_table(), width=8),
                ],
            ),
            dbc.Row(
                [                 
                    dbc.Col(
                        [
                            html.Button('Generate PDF', id='generate-pdf-button'),
                            html.Div(id='generate-pdf-result'),
                        ]
                    ),
                    dbc.Col(display_iframe())
                ],
            ),
        ]
    )

# Create a callback function to trigger the Flask endpoint
@app.callback(
    Output('generate-pdf-result', 'children'),
    [Input('generate-pdf-button', 'n_clicks')]
)
def on_generate_pdf_click(n_clicks):
    if n_clicks is not None:
        response = requests.post('http://localhost:8050/generate_pdf')
        result = response.json()
        return result['message']
    return ''
    
# Generate PDF Flask endpoint
# Starts up a node.js subprocess that runs a Puppeteer script
@app.server.route('/generate_pdf', methods=['POST'])
def run_generate_pdf():
    print("run_generate_pdf invoked")
    try:
        subprocess.check_call(['node', 'generate_pdf.js'])
        return {'status': 'success', 'message': 'PDF generated successfully'}
    except subprocess.CalledProcessError as error:
        print(f'Error occurred: {error}')
        return {'status': 'error', 'message': 'Error generating PDF'}

if __name__ == "__main__":
    app.run_server(debug=True)