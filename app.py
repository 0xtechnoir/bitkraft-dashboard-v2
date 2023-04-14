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
from views.btc_futures_aggregated_open_interest import display_btc_futures_agg_open_interest_chart
from views.eth_futures_aggregated_open_interest import display_eth_futures_agg_open_interest_chart
from views.fear_and_greed_index import display_fear_and_greed_chart
from views.fed_liquidity_index import display_fed_liquidity_index_chart

server = app.server
app.layout = html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(display_treasury_yield_curve(), width=4, style={'height': '100%', 'overflow': 'auto'}),
                    dbc.Col(display_dxy(), width=4, style={'height': '100%', 'overflow': 'auto'}),
                    dbc.Col(display_brent(), width=4, style={'height': '100%', 'overflow': 'auto'})
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
                    dbc.Col(display_btc_pearson_correlation(), width=6),
                    dbc.Col(display_fear_and_greed_chart(), width=6)
                ],
            ),
            dbc.Row(
                [                 
                    dbc.Col(display_nft_collection_ranking_table(), width=8),
                    
                ],
            ),
             dbc.Row(
                [                 
                    dbc.Col(display_btc_futures_agg_open_interest_chart(), width=6),
                    dbc.Col(display_eth_futures_agg_open_interest_chart(), width=6),
                ],
            ),
            dbc.Row(
                [                 
                    dbc.Col(display_fed_liquidity_index_chart(), width=6),
                ],
            ),
            dbc.Row(
                [                 
                    dbc.Col(
                        html.Iframe(
                           width="100%", 
                           height="420", 
                           src="https://embed.theblockcrypto.com/data/crypto-markets/options/aggregated-open-interest-of-bitcoin-options/embed",
                           title="Aggregated Open Interest of Bitcoin Options"
                        ), width=6
                    ),
                    dbc.Col(
                        html.Iframe(
                           width="100%", 
                           height="420", 
                           src="https://embed.theblockcrypto.com/data/crypto-markets/options/btc-put-call-ratio/embed",
                           title="BTC Put/Call Ratio"
                        ), width=6
                    ),
                ],
            ),
            dbc.Row(
                [                 
                    dbc.Col(
                        html.Iframe(
                           width="100%", 
                           height="420", 
                           src="https://embed.theblockcrypto.com/data/crypto-markets/options/aggregated-open-interest-of-ethereum-options/embed",
                           title="Aggregated Open Interest of Ethereum Options"
                        ), width=6
                    ),
                    dbc.Col(
                        html.Iframe(
                           width="100%", 
                           height="420", 
                           src="https://embed.theblockcrypto.com/data/crypto-markets/options/eth-put-call-ratio/embed",
                           title="ETH Put/Call Ratio"
                        ), width=6
                    ),
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