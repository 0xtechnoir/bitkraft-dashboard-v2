from dash import html
from maindash import app

def weekly_web3_gaming_vol():
    return html.Iframe(
        src="https://www.footprint.network/public/chart/Weekly-GameFi-Volume-fp-c138a176-0b3b-4488-b1c1-4d4459d5fe25",
        width="1800",
        height="600",
    )