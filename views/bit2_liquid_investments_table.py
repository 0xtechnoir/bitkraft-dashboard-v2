from maindash import app
from utilities.read_google_sheets import read_google_sheet
from dash import html, dash_table
import pymongo
import pandas as pd
import os
import datetime
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv
load_dotenv()

MONGODB_CONNECTION = os.getenv('MONGODB_CONNECTION')

coinIds = ["karate-combat"]
labels = ["KARATE"]

costBasis = {
  "KARATE": 0.0005,
}

client = pymongo.MongoClient(MONGODB_CONNECTION)
db = client["historical_price_data"]

#  create a new dataframe for the table
df_table = pd.DataFrame(columns=['Token', 'Tokens Held', 'Avg. Token Price ($)','Cost Basis ($)', 'Current Value ($)', 'ROI'])

# Pull liquid token data
sheetId = '1wm5Whcdxm7FDBsNeQsJqXtPXJ7tDf6JrjY3EDBlQZPU'
range = 'Market Report - Liquid Investment Tables!A1:D2'
sheet_values = read_google_sheet(sheetId, range)
if sheet_values:
    sheet_headers = sheet_values[0]
    sheet_data = sheet_values[1:]
    sheet_df = pd.DataFrame(sheet_data, columns=sheet_headers)
else:
    sheet_df = pd.DataFrame()

# retrieve the current price of the KARATE token from mongodb
col = db[coinIds[0]]
cursor = col.find({}, {"_id":0, "time":1, "usd_value":1})
# Convert the cursor to a list of dictionaries, then to a dataframe
li = list(cursor)
df1 = pd.DataFrame(li)
df1['date'] = pd.to_datetime(df1["time"], unit="ms")
current_price = df1['usd_value'].iloc[-1]

# map the values from sheet_df to the df_table
for index, row in sheet_df.iterrows():
    name = row['token']
    tokens_held = int(row['tokens_held'])
    # format to use comma separators for thousands and hundreds

    token_price_at_cost = float(row['avg_token_price'])
    value_at_cost = int(row['cost_basis'])
    roi = ((current_price - token_price_at_cost) / token_price_at_cost) * 100
    current_value = int(current_price*tokens_held) if current_price is not None else '-'

    new_entry = {
        'Token': name,
        'Tokens Held': "{:,}".format(tokens_held),
        'Avg. Token Price ($)': "{:,.7f}".format(token_price_at_cost),
        'Cost Basis ($)': "{:,}".format(value_at_cost),
        'Current Value ($)': "{:,}".format(current_value),
        'ROI': int(round(roi))
    }

    df_table.loc[labels[index]] = new_entry

formatNum = lambda x: round(x, 4) if isinstance(x, (float)) else x

def formatCell(val, column):
    if isinstance(val, (int, float)) and val < 0:
        return f'({abs(val)}{ "%" if column in ["ROI"] else ""})'
    elif isinstance(val, (int, float)):
        return f'{val}{ "%" if column in ["ROI"] else ""}'
    else:
        return val

df = df_table.applymap(formatNum).apply(lambda x: x.map(lambda y: formatCell(y, x.name)))

def display_bit2_liquid_investments():

    return html.Div([
        html.H4('BIT2 Liquid Investments', style={'text-align': 'left'}),
        dash_table.DataTable(
            columns=[{"name": i, "id": i} for i in df.columns],
            data=df.to_dict("records"),
            style_cell={
                'textAlign': 'center',
                'padding': '0px 15px'
            },
            style_data_conditional=[
                {
                    'if': {'column_id': c, 'filter_query': '{{{}}} contains "("'.format(c)},
                    'color': 'red'
                } for c in ['ROI']
            ],
            style_header={
                'fontWeight': 'bold',
                'backgroundColor': '#46637f',
                'color': 'white',
            },
        ),
    ])