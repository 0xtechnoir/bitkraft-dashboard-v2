from dash import html
from maindash import app

def top_web3_games():
    return html.Iframe(
        src="https://www.footprint.network/public/chart/Top-Web3-Games-Ranked-by-Avg-DAU-(7D)-fp-f74baba5-e95d-4079-9e4c-b151f5087249",
        width="1800",
        height="600",
    )