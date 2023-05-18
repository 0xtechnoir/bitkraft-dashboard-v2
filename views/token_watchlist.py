from maindash import app
from dash import html, dash_table
import pymongo
import pandas as pd
import os
import datetime
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv
load_dotenv()

MONGODB_CONNECTION = os.getenv('MONGODB_CONNECTION')

client = pymongo.MongoClient(MONGODB_CONNECTION)
db = client["historical_price_data"]
col = db['token_watchlist']
cursor = col.find()
df = pd.DataFrame(list(cursor))
df['fdv'] = pd.to_numeric(df['fdv'], errors='coerce')
df.sort_values('fdv', ascending=False, inplace=True)
df.drop(columns=['_id','coin_id', 'rank'], inplace=True)
df['price'] = df['price'].astype(float).round(3)

# Rename columns 
df.rename(columns={
    'token': 'Ticker',
    'price': "Price ($)",
    'price_change_pc_24hr': '24H',
    'price_change_pc_7d': '7D',
    'price_change_pc_30d': '30D',
    'price_change_pc_3m': '3M',
    'price_change_pc_6m': '6M',
    'volume_24h': '24H Vol ($)',
    'market_cap': 'MC ($)',
    'fdv': 'FDV ($)',
    'circulating_supply': 'Circ. Supply',
    'total_supply': 'Total Supply',
    'max_supply': 'Max Supply',
    'pc_circulating': 'Circ'
}, inplace=True)

def convert_to_shorthand(n):
    if pd.isna(n): # Keep NaN values as is
        return n
    if isinstance(n, str): # If the value is already a string, convert it to float first
        n = float(n.replace(',', ''))
    if n >= 10**9: # Convert billion to B
        return str(round(n / 10**9, 2)) + 'B'
    if n >= 10**6: # Convert million to M
        return str(round(n / 10**6, 2)) + 'M'
    if n >= 10**3: # Convert thousand to K
        return str(round(n / 10**3, 2)) + 'K'
    return str(n) # If less than thousand, return as is

# Apply the function to necessary columns
for col in ['24H Vol ($)', 'MC ($)', 'FDV ($)', 'Circ. Supply', 'Total Supply', 'Max Supply']:
    df[col] = df[col].apply(convert_to_shorthand)

# Apply '%' to 'CIRC' column and remove decimal places
df['Circ'] = df['Circ'].apply(lambda x: str(int(x)) + '%' if pd.notna(x) and isinstance(x, (int, float)) else x)

# Finally, convert any null values to a '-'
df = df.fillna('-')

def display_token_watchlist():
    
    column_styles = []

    for col in df.columns:
        if 'Change' in col:
            column_styles.append({
                'if': {'column_id': col},
                'backgroundColor': 'darkblue',
                'color': 'white'
            })
        elif 'FDV' in col:
            column_styles.append({
                'if': {'column_id': col},
                'backgroundColor': 'lightblue',
                'color': 'black'
            })

    # Define your columns here
    columns = [
        {"name": ["", "Ticker"], "id": "Ticker"},
        {"name": ["", "Price ($)"], "id": "Price ($)"},
        {"name": ["", "24H Vol ($)"], "id": "24H Vol ($)"},
        {"name": ["Change", "24H"], "id": "24H"},
        {"name": ["Change", "7D"], "id": "7D"},
        {"name": ["Change", "30D"], "id": "30D"},
        {"name": ["Change", "3M"], "id": "3M"},
        {"name": ["Change", "6M"], "id": "6M"},
        {"name": ["", "MC ($)"], "id": "MC ($)"},
        {"name": ["", "FDV ($)"], "id": "FDV ($)"},
        {"name": ["Supply", "Circ. Supply"], "id": "Circ. Supply"},
        {"name": ["Supply", "Total Supply"], "id": "Total Supply"},
        {"name": ["Supply", "Max Supply"], "id": "Max Supply"},
        {"name": ["Supply", "Circ"], "id": "Circ"},
    ]

    return html.Div([
        html.H4('Token Watchlist', style={'text-align': 'left'}),
        dash_table.DataTable(
            columns=columns,
            data=df.to_dict("records"),
            style_cell={
                'textAlign': 'center',
                'padding': '0px 15px'
            },
            style_data_conditional=[
                {
                    'if': {'column_id': c, 'filter_query': '{{{}}} contains "("'.format(c)},
                    'color': 'red'
                } for c in ['24H','7D','30D','3M','6M']
            ] + [
                {
                    'if': {'column_id': c},
                    'backgroundColor': '#e8f4ff' 
                } for c in ['24H', '7D', '30D', '3M', '6M', 'Circ. Supply', 'Total Supply', 'Max Supply', 'Circ']
            ],
            style_header={'fontWeight': 'bold'},
            style_header_conditional=[
                {
                    'if': {
                        'column_id': c,
                        'header_index': 0
                    },
                    'textAlign': 'center',
                    'backgroundColor': '#46637f',
                    'color': 'white',
                } for c in ['24H', '7D', '30D', '3M', '6M', 'Circ. Supply', 'Total Supply', 'Max Supply', 'Circ']
            ] 
            + [
                 {
                    'if': {
                        'column_id': c,
                    },
                    'textAlign': 'center',
                    'backgroundColor': '#46637f',
                    'color': 'white',
                } for c in ['Ticker', 'Price ($)', '24H Vol ($)', 'MC ($)', 'FDV ($)']
            ]
            + [
                 {
                    'if': {
                        'column_id': c,
                        'header_index': 1
                    },
                    'textAlign': 'center',
                    'backgroundColor': '#3C7CA6'
                } for c in ['24H', '7D', '30D', '3M', '6M', 'Circ. Supply', 'Total Supply', 'Max Supply', 'Circ']
            ],
            merge_duplicate_headers=True,
        ),
    ])


