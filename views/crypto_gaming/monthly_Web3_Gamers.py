from dash import html
from maindash import app

def monthly_web3_gamers():
    return html.Iframe(
        src="https://www.footprint.network/public/chart/Monthly-GameFi-Users-fp-8003b8ec-17f0-48a9-be3b-291977977053",
        width="1800",
        height="600",
    )