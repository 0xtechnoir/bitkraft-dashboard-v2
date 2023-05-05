import pandas as pd
from dash import html, dash_table
import pymongo
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()
MONGODB_CONNECTION = os.getenv('MONGODB_CONNECTION')
client = pymongo.MongoClient(MONGODB_CONNECTION)
db = client["historical_price_data"]
col = db['nft_collection_ranking']

pd.set_option('display.float_format', '{:,.2f}'.format)

column_names = [
    "Rank",
    "Name", 
    "7D Vol ($)", 
    "Market Cap ($)", 
    "Floor (Ξ)", 
    "Floor ($)",  
    "24H Floor Chg %",
    "7D Floor Chg %",
    "30D Floor Chg %",
    "Total Supply",
    "Holders",
]

df = pd.DataFrame(columns=column_names)
sorted_records = col.find().sort("Rank", 1).limit(20)

blend_collections = ["Milady Maker", "Wrapped Cryptopunks", "Azuki"]

for record in sorted_records:

    name = record['name']
    if name in blend_collections:
        name += " (B)"

    new_row = pd.DataFrame([{
        'Rank': record['Rank'],
        'Name': name,
        '7D Vol ($)': record['volume_usd'],
        "Market Cap ($)": record['market_cap_usd'],
        "Floor (Ξ)": record['floor_price_eth'],
        "Floor ($)": record['floor_price_usd'],
        "24H Floor Chg %": record['floor_change_24hr'],
        "7D Floor Chg %": record['floor_change_7d'],
        "30D Floor Chg %": record['floor_change_30d'],
        "Total Supply": record['total_supply'],
        "Holders": record['holder_num'],
    }], columns=column_names)

    df = pd.concat([df, new_row], ignore_index=True)

formatNum = lambda x: round(x, 2) if isinstance(x, (float)) else x
    
def formatCell(val, column):
    no_decimal_columns = ['Rank', '7D Vol', 'Market Cap', 'Floor $', 'Total Supply', 'Holders']
    if pd.isna(val):
        return "-"
    elif isinstance(val, (int, float)) and val < 0:
        return f'({abs(val):,.0f}{ "%" if column in ["24H Floor Chg %", "7D Floor Chg %", "30D Floor Chg %"] else ""})' if column in no_decimal_columns else f'({abs(val):,.2f}{ "%" if column in ["24H Floor Chg %", "7D Floor Chg %", "30D Floor Chg %"] else ""})'
    elif isinstance(val, (int, float)):
        return f'{val:,.0f}{ "%" if column in ["24H Floor Chg %", "7D Floor Chg %", "30D Floor Chg %"] else ""}' if column in no_decimal_columns else f'{val:,.2f}{ "%" if column in ["24H Floor Chg %", "7D Floor Chg %", "30D Floor Chg %"] else ""}'
    else:
        return val

df_table = df.applymap(formatNum).apply(lambda x: x.map(lambda y: formatCell(y, x.name)))

def display_nft_collection_ranking_table():
    return html.Div([
        html.H4('Top NFT collections (7D Vol)', style={'text-align': 'left'}),
        dash_table.DataTable(
            columns=[{"name": i, "id": i} for i in df_table.columns],
            data=df_table.to_dict("records"),
            style_cell={
                'textAlign': 'left' if column == 'Name' else 'center'
                for column in df_table.columns
            },
            style_data_conditional=[
                {
                    'if': {'column_id': 'Name'},
                    'textAlign': 'left',
                },
                *[
                    {
                        'if': {'column_id': c, 'filter_query': '{{{}}} contains "("'.format(c)},
                        'color': 'red'
                    } for c in ["24H Floor Chg %", "7D Floor Chg %", "30D Floor Chg %"]        
                ],
                *[
                    {
                        'if': {'row_index': i, 'column_id': c},
                        'backgroundColor': '#E0F0FF'
                    }
                    for i, row in df_table.iterrows()
                    for c in df_table.columns
                    if row["Name"].endswith("(B)")
                ],
            ],
            style_header={'fontWeight': 'bold'},
        ),
        html.P('(B) = Collection available on Blend (Blur lending)')
    ])

