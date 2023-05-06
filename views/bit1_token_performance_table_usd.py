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

coinIds = ["yield-guild-games", "alethea-artificial-liquid-intelligence-token",
    "immutable-x", "rainbow-token-2", "superfarm", "matic-network", "sipher", "blackpool-token"]

labels = ["YGG", "ALI", "IMX", "RBW", "SUPER", "MATIC", "SIPHER", "BPT"]

costBasis = {
  "YGG": 0.047,
  "ALI": 0.01,
  "IMX": 0.0256,
  "RBW": 0.0228,
  "SUPER": 0.18,
  "MATIC": 0.9,
  "SIPHER": 0.06,
  "BPT": 2.0,
}

client = pymongo.MongoClient(MONGODB_CONNECTION)
db = client["historical_price_data"]

#  create a new dataframe for the table
df_table = pd.DataFrame(columns=['Token', 'Cost Basis', 'Current', 'ROI', 'Tokens Vested', 'Tokens Vested ($)', 'Prior Week', 'Prior Year', 'Weekly Change', 'YTD Change', 'YoY Change'])

# Pull token vesting data
sheet_values = read_google_sheet()
if sheet_values:
    sheet_headers = sheet_values[0]
    sheet_data = sheet_values[1:]
    df_sheet = pd.DataFrame(sheet_data, columns=sheet_headers)
else:
    df_sheet = pd.DataFrame()

print(df_sheet)
                                
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
        vested_tokens_percent = matching_row['Total Vested Token Accumulated (%)'].iloc[0]
        vested_tokens_dollar = matching_row['Total Vested Token Accumulated ($)'].iloc[0]
    else:
        vested_tokens_percent = None
        vested_tokens_dollar = None

    new_entry = {
        'Token': name,
        'Cost Basis': cb,
        'Current': current_price,
        'ROI': int(round(roi)),
        'Tokens Vested': float(vested_tokens_percent) if vested_tokens_percent is not None else '-',
        'Tokens Vested ($)': format('{:,.0f}'.format(float(vested_tokens_dollar))) if vested_tokens_dollar is not None else None,
        'Prior Week': prior_week_price,
        'Prior Year': prior_year_price,
        'Weekly Change': ((current_price - prior_week_price)/prior_week_price)*100,
        'YTD Change': ((current_price - ytd_price)/ytd_price)*100,
        'YoY Change': ((current_price - prior_year_price)/prior_year_price)*100 if prior_year_price != '-' else '-'
    }

    df_table.loc[labels[index]] = new_entry

formatNum = lambda x: round(x, 2) if isinstance(x, (float)) else x

def formatCell(val, column):
    # if val is None:
    #     return '-' if column in ["Tokens Vested", "Tokens Vested ($)"] else None
    if isinstance(val, (int, float)) and val < 0:
        return f'({abs(val)}{ "%" if column in ["ROI", "Weekly Change", "YTD Change", "YoY Change", "Tokens Vested"] else ""})'
    elif isinstance(val, (int, float)):
        return f'{val}{ "%" if column in ["ROI", "Weekly Change", "YTD Change", "YoY Change", "Tokens Vested"] else ""}'
    else:
        return val

print(df_table)

df = df_table.applymap(formatNum).apply(lambda x: x.map(lambda y: formatCell(y, x.name)))

print(df)
def display_bit1_portfolio_table_usd():

    return html.Div([
        html.H4('BIT1 Portfolio ($ Denominated)', style={'text-align': 'left'}),
        dash_table.DataTable(
            columns=[{"name": i, "id": i} for i in df.columns],
            data=df.to_dict("records"),
            style_cell={'textAlign': 'center'},
            style_data_conditional=[
                {
                    'if': {'column_id': c, 'filter_query': '{{{}}} contains "("'.format(c)},
                    'color': 'red'
                } for c in ['ROI', 'Weekly Change', 'YTD Change', 'YoY Change']
            ],
            style_header={'fontWeight': 'bold'},
        ),
        html.P('Note: SUPER token option at $0.18 not yet executed')
    ])