from maindash import app
from dash import html, dash_table
import pymongo
import pandas as pd
import os
import datetime
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
df_table = pd.DataFrame(columns=['Token', 'Cost Basis', 'Current', 'ROI', 'Prior Week', 'YTD', 'Prior Year', 'Weekly Change', 'YTD Change', 'YoY Change'])

today = datetime.date.today()
day_of_year = today.timetuple().tm_yday

# Loop through the coinIds and create a dataframe for each coin
for index, coin in enumerate(coinIds):
    col = db[coinIds[index]]
    cursor = col.find({}, {"_id":0, "time":1, "usd_value":1})
    # Convert the cursor to a list of dictionaries, then to a dataframe
    li = list(cursor)
    df1 = pd.DataFrame(li)
    df1['date'] = pd.to_datetime(df1["time"], unit="ms")
    current_price = df1['usd_value'].iloc[-1]
    prior_week_price = df1['usd_value'].iloc[-8]
    ytd_price = df1['usd_value'].iloc[-day_of_year]
    prior_year_price = df1['usd_value'].iloc[-366] if len(df1) >= 366 else '-' 
    name = labels[index]
    cb = costBasis.get(name) 
    roi = ((current_price - cb) / cb) * 100

    new_entry = {
        'Token': name,
        'Cost Basis': cb,
        'Current': current_price,
        'ROI': int(round(roi)),
        'Prior Week': prior_week_price,
        'YTD': ytd_price,
        'Prior Year': prior_year_price,
        'Weekly Change': ((current_price - prior_week_price)/prior_week_price)*100,
        'YTD Change': ((current_price - ytd_price)/ytd_price)*100,
        'YoY Change': ((current_price - prior_year_price)/prior_year_price)*100 if prior_year_price != '-' else '-'
    }

    df_table.loc[labels[index]] = new_entry

formatNum = lambda x: round(x, 2) if isinstance(x, (float)) else x

# For negative values, remove sign and add brackets. Add % symbol to relevant values 
def formatCell(val, column):
    if isinstance(val, (int, float)) and val < 0:
        return f'({abs(val)}{ "%" if column in ["ROI", "Weekly Change", "YTD Change", "YoY Change"] else ""})'
    elif isinstance(val, (int, float)):
        return f'{val}{ "%" if column in ["ROI", "Weekly Change", "YTD Change", "YoY Change"] else ""}'
    else:
        return val

df = df_table.applymap(formatNum).apply(lambda x: x.map(lambda y: formatCell(y, x.name)))

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