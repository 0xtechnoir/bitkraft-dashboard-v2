import dash
import pandas as pd
import pymongo
import dash_bootstrap_components as dbc

data = pd.read_csv("avocado.csv")
data["Date"] = pd.to_datetime(data["Date"], format="%Y-%m-%d")
data.sort_values("Date", inplace=True)

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Bitkraft Analytics"