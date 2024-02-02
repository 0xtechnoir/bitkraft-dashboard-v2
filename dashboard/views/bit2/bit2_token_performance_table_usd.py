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
df_table = pd.DataFrame(columns=['Token', 'Cost Basis ($)', 'Current ($)', 'Vested', 'Realized ($)', 'Unrealized ($)', 'Prior Week ($)', 'Prior Year ($)', '7D Change', 'YTD Change', 'YoY Change', 'ROI'])

# Pull token vesting data
sheet_id = '1wm5Whcdxm7FDBsNeQsJqXtPXJ7tDf6JrjY3EDBlQZPU'
cellRange = 'Market Report!A2:E3'
sheet_values = read_google_sheet(sheet_id, cellRange)
if sheet_values:
    sheet_headers = sheet_values[0]
    sheet_data = sheet_values[1:]
    df_sheet = pd.DataFrame(sheet_data, columns=sheet_headers)
else:
    df_sheet = pd.DataFrame()
                                
today = datetime.date.today()
day_of_year = today.timetuple().tm_yday
one_week_ago = today - datetime.timedelta(days=7)
jan_1st = datetime.date(today.year, 1, 1)
one_year_ago = today - relativedelta(years=1)

# Loop through the coinIds and create a dataframe for each coin
for index, coin in enumerate(coinIds):
    col = db[coinIds[index]]
    cursor = col.find({}, {"_id":0, "time":1, "usd_value":1})
    # Convert the cursor to a list of dictionaries, then to a dataframe
    li = list(cursor)
    df1 = pd.DataFrame(li)
    df1['date'] = pd.to_datetime(df1["time"], unit="ms")  
    current_price = df1['usd_value'].iloc[-1]    
    prior_week_price_df = df1[df1['date'].dt.date == one_week_ago]
    prior_week_price = prior_week_price_df['usd_value'].iloc[0] if not prior_week_price_df.empty else None
    ytd_price_df = df1[df1['date'].dt.date == jan_1st]
    ytd_price = ytd_price_df['usd_value'].iloc[0] if not ytd_price_df.empty else None
    prior_year_price_df = df1[df1['date'].dt.date == one_year_ago]
    prior_year_price = prior_year_price_df['usd_value'].iloc[0] if not prior_year_price_df.empty else None
    name = labels[index]
    cb = costBasis.get(name) 
    roi = ((current_price - cb) / cb) * 100

    matching_row = df_sheet[df_sheet['Ticker'] == name]
    if not matching_row.empty:
        vested = matching_row['Vested'].iloc[0]
        realised = matching_row['Realized'].iloc[0]
        unrealised = matching_row['Unrealized'].iloc[0]
    else:
        vested = None
        realised = None
        unrealised = None

    print(f'Coin: {name}, Unrealised: {unrealised}, Typeof Unrealized: {type(unrealised)}')

    new_entry = {
        'Token': name,
        'Cost Basis ($)': '{:,.4f}'.format(cb),
        'Current ($)': '{:,.5f}'.format(current_price),
        'Vested': float(vested)*100 if vested is not None else '-',
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
        return f'({abs(val)}{ "%" if column in ["ROI", "7D Change", "YTD Change", "YoY Change", "Vested"] else ""})'
    elif isinstance(val, (int, float)):
        return f'{val}{ "%" if column in ["ROI", "7D Change", "YTD Change", "YoY Change", "Vested"] else ""}'
    return val

df = df_table.applymap(formatNum).apply(lambda x: x.map(lambda y: formatCell(y, x.name)))

def display_bit2_portfolio_table_usd():

    return html.Div([
        html.H4('BIT2 Portfolio ($ Denominated)', style={'text-align': 'left'}),
        dash_table.DataTable(
            columns=[{"name": i, "id": i} for i in df.columns],
            # ensure the table is always 80% width of the screen
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
                } for c in ['ROI', '7D Change', 'YTD Change', 'YoY Change']
            ],
            style_header={
                'fontWeight': 'bold',
                'backgroundColor': '#46637f',
                'color': 'white',
            },
        ),
    ],style={'margin': '20px'})