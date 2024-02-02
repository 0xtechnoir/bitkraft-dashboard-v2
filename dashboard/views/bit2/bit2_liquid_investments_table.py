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

client = pymongo.MongoClient(MONGODB_CONNECTION)
db = client["historical_price_data"]

#  create a new dataframe for the table
df_table = pd.DataFrame(columns=['Token', 'Cost Basis ($)', 'Current ($)', 'Tokens Held', 'Realized ($)', 'Unrealized ($)', 'Prior Week ($)', 'Prior Year ($)', '7D Change', 'YTD Change', 'YoY Change', 'ROI'])

# Pull liquid token data
sheetId = '1wm5Whcdxm7FDBsNeQsJqXtPXJ7tDf6JrjY3EDBlQZPU'
cellRange = 'Market Report!A11:G12'
sheet_values = read_google_sheet(sheetId, cellRange)
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


today = datetime.date.today()
day_of_year = today.timetuple().tm_yday
one_week_ago = today - datetime.timedelta(days=7)
jan_1st = datetime.date(today.year, 1, 1)
one_year_ago = today - relativedelta(years=1)

# map the values from sheet_df to the df_table
for index, row in sheet_df.iterrows():
    name = row['token']
    tokens_held = int(row['tokens_held'])
    # format to use comma separators for thousands and hundreds

    token_price_at_cost = float(row['avg_token_price'])
    value_at_cost = int(row['cost_basis'])
    current_price = df1['usd_value'].iloc[-1]    
    roi = ((current_price - token_price_at_cost) / token_price_at_cost) * 100
    current_value = int(current_price*tokens_held) if current_price is not None else '-'

    prior_week_price_df = df1[df1['date'].dt.date == one_week_ago]
    prior_week_price = prior_week_price_df['usd_value'].iloc[0] if not prior_week_price_df.empty else None
    ytd_price_df = df1[df1['date'].dt.date == jan_1st]
    ytd_price = ytd_price_df['usd_value'].iloc[0] if not ytd_price_df.empty else None
    prior_year_price_df = df1[df1['date'].dt.date == one_year_ago]
    prior_year_price = prior_year_price_df['usd_value'].iloc[0] if not prior_year_price_df.empty else None


    matching_row = sheet_df[sheet_df['Ticker'] == name]
    if not matching_row.empty:
        realised = matching_row['Realized'].iloc[0]
        unrealised = matching_row['Unrealized'].iloc[0]
    else:
        realised = None
        unrealised = None

    new_entry = {
        'Token': name,
        'Cost Basis ($)': "{:,.7f}".format(token_price_at_cost),
        'Current ($)': '{:,.5f}'.format(current_price),
        'Tokens Held': "{:,}".format(tokens_held),
        'Realized ($)': '{:,.0f}'.format(float(realised)) if realised is not None else '-',
        'Unrealized ($)': '{:,.0f}'.format(float(unrealised)) if unrealised is not None else '-',
        'Prior Week ($)': '{:,.5f}'.format(prior_week_price) if prior_week_price is not None else '-',
        'Prior Year ($)': '{:,.5f}'.format(prior_year_price) if prior_year_price is not None else '-',
        '7D Change': ((current_price - prior_week_price)/prior_week_price)*100 if prior_week_price is not None else '-',
        'YTD Change': ((current_price - ytd_price)/ytd_price)*100 if ytd_price is not None else '-',
        'YoY Change': ((current_price - prior_year_price)/prior_year_price)*100 if prior_year_price is not None else '-',
        'ROI': int(round(roi)),
    }

    df_table.loc[labels[index]] = new_entry

# add empty rows to the dataframe if there are less than 3 rows
if len(df_table) < 3:
    missing_rows = 4 - len(df_table)
    empty_df = pd.DataFrame(index=range(missing_rows), columns=df_table.columns)
    df_table = pd.concat([df_table, empty_df])

def formatNum(x):
    if pd.isna(x):
        return ' '
    elif isinstance(x, float):
        return round(x, 4)
    return x

def formatCell(val, column):
    if pd.isna(val):
        return ' '
    elif isinstance(val, (int, float)) and val < 0:
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
            style_table={'width': '100%'},
            data=df.to_dict("records"),
            style_cell={
                'textAlign': 'center',
                'padding': '0px 15px',
                'fontSize': '20px',
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
    ],style={'margin': '20px'})