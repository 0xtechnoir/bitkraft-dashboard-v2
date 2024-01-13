from dash import html
from maindash import app
import requests
import subprocess
from flask import request
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

#  Views - Individual Charts
from views.macro.treasury_yield_curve import display_treasury_yield_curve
from views.macro.dxy import display_dxy
from views.macro.brent import display_brent
from views.macro.gold import display_gold
from views.macro.ftse100 import display_ftse
from views.macro.sp500 import display_sp500
from views.macro.nasaq import display_nasdaq
from views.macro.hangseng import display_hangseng
from views.macro.gaming_equities import display_gaming_equities
from views.bit1.bit1_portfolio import display_bit1_portfolio
from views.bit2.bit2_portfolio import display_bit2_portfolio
from views.crypto_market.btc import display_btc
from views.crypto_market.eth import display_eth
from views.crypto_market.crypto_price_performance_30d import display_crypto_price_performance_30d_chart
from views.bit1.bit1_token_performance_table_usd import display_bit1_portfolio_table_usd
from views.bit2.bit2_token_performance_table_usd import display_bit2_portfolio_table_usd
from views.crypto_market.btc_pearson_correlation import display_btc_pearson_correlation
from views.nfts.nft_rankings import display_nft_collection_ranking_table
from views.crypto_gaming.monthly_Web3_Gamers import monthly_web3_gamers
from views.crypto_gaming.weekly_web3_gaming_vol import weekly_web3_gaming_vol
from views.crypto_gaming.top_web3_games import top_web3_games
from views.crypto_market.btc_futures_aggregated_open_interest import display_btc_futures_agg_open_interest_chart
from views.crypto_market.eth_futures_aggregated_open_interest import display_eth_futures_agg_open_interest_chart
from views.crypto_market.fear_and_greed_index import display_fear_and_greed_chart
from views.crypto_market.fear_and_greed_meter import display_fear_and_greed_meter
from views.macro.fed_liquidity_index import display_fed_liquidity_index_chart
from views.crypto_market.annualized_btc_volatility_30d import display_btc_annualized_volatility_30d
from views.watchlists.token_watchlist import display_token_watchlist
from views.bit2.bit2_liquid_investments_table import display_bit2_liquid_investments

server = app.server
app.layout = html.Div(
        [
            dbc.Row(
                [                 
                    dbc.Col(
                        [
                            html.Button('Generate PDF', id='generate-pdf-button'),
                            html.Div(id='generate-pdf-result'),
                        ]
                    ),
                ],
            ),
            html.H1('BIT1 Overview', style={'text-align': 'center'}),
            dbc.Row(
                [
                    dbc.Col(display_bit1_portfolio(), width=12),
                ],
            ),
            dbc.Row(
                [
                    dbc.Col(display_bit1_portfolio_table_usd(), width=12),
                ],
            ),
            html.Br(),
            html.H1('BIT2 Overview', style={'text-align': 'center'}),
            dbc.Row(
                [
                    dbc.Col(display_bit2_portfolio(), width=12),
                ],
            ),
            dbc.Row(
                [
                    dbc.Col(display_bit2_portfolio_table_usd(), width=12),
                ],
            ),
            html.Br(),
            dbc.Row(
                [
                    dbc.Col(display_bit2_liquid_investments(), width=12),
                ],
            ),
            html.Br(),
            html.H1('Treasury, Currency and Equities', style={'text-align': 'center'}),
            dbc.Row(
                [
                    dbc.Col(display_treasury_yield_curve(), width=3),
                    dbc.Col(display_fed_liquidity_index_chart(), width=6),                    
                    dbc.Col(display_dxy(), width=3),
                ],
            ),
            dbc.Row(
                [                    
                    dbc.Col(display_brent(), width=3),
                    dbc.Col(display_gold(), width=3),
                    dbc.Col(display_ftse(), width=3),
                    dbc.Col(display_sp500(), width=3),
                ],
            ),
            dbc.Row(
                [
                    dbc.Col(display_nasdaq(), width=3),
                    dbc.Col(display_hangseng(), width=3),
                    dbc.Col(display_gaming_equities(), width=6),
                    
                ],
            ),
            html.Br(),
            html.H1('Token Watchlist', style={'text-align': 'center'}),
            dbc.Row(
                [
                    dbc.Col(display_token_watchlist(), width=12),
                ],
            ),
            html.Br(),
            html.H1('Crypto Market', style={'text-align': 'center'}),
            dbc.Row(
                [                 
                    dbc.Col(display_crypto_price_performance_30d_chart(), width=12),
                ],
            ),
            dbc.Row(
                [                 
                    dbc.Col(display_btc(), width=6),
                    dbc.Col(display_eth(), width=6),
                ],
            ),
            dbc.Row(
                [                 
                    dbc.Col(display_btc_pearson_correlation(), width=12),
                ],
            ),
            dbc.Row(
                [                 
                    dbc.Col(
                        html.Iframe(
                           width="100%", 
                           height="420", 
                           src="https://www.theblock.co/data/crypto-markets/spot/cryptocurrency-exchange-volume-monthly/embed",
                           title="Cryptocurrency Monthly Exchange Volume"
                        ), width=4
                    ),
                    dbc.Col(
                        html.Iframe(
                           width="100%", 
                           height="420", 
                           src="https://www.theblock.co/data/crypto-markets/spot/total-exchange-volume-daily/embed",
                           title="Daily Exchange Volume (7DMA)"
                        ), width=4
                    ),
                    dbc.Col(
                        html.Iframe(
                           width="100%", 
                           height="420", 
                           src="https://www.theblock.co/data/crypto-markets/spot/usd-support-exchange-volume/embed",
                           title="USD Support Exchange Volume"
                        ), width=4
                    ),
                ],
            ),
             dbc.Row(
                [                 
                    dbc.Col(display_fear_and_greed_chart(), width=8),
                    dbc.Col(display_fear_and_greed_meter(), width=4)

                ],
            ),
            dbc.Row(
                [                 
                    dbc.Col(display_btc_annualized_volatility_30d(), width=12),
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
                    dbc.Col(display_nft_collection_ranking_table(), width=12),
                ],
            ),
            dbc.Row(
                [                 
                    dbc.Col(weekly_web3_gaming_vol())
                ],
            ),
            dbc.Row(
                [                 
                    dbc.Col(monthly_web3_gamers())
                ],
            ),
            dbc.Row(
                [                 
                    dbc.Col(top_web3_games())
                ],
            ),
        ],
        style={'backgroundColor': '#FFFFFF'}
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