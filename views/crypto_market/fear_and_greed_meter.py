from dash import html
from maindash import app

def display_fear_and_greed_meter():
    return html.Iframe(
        src="https://embeds.simple.ink/custom/fear-and-greed-index-1665743361",
        width="460",
        height="450",
    )