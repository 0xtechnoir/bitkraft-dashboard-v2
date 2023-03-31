from maindash import app
from dash import html, dash_table
import pymongo
import pandas as pd
import os
import datetime
from dotenv import load_dotenv
from math import log10, floor

load_dotenv()
MONGODB_CONNECTION = os.getenv('MONGODB_CONNECTION')

coinIds = ["yield-guild-games", "alethea-artificial-liquid-intelligence-token",
    "immutable-x", "rainbow-token-2", "superfarm", "matic-network", "sipher", "blackpool-token"]

labels = ["YGG", "ALI", "IMX", "RBW", "SUPER", "MATIC", "SIPHER", "BPT"]

client = pymongo.MongoClient(MONGODB_CONNECTION)
db = client["historical_price_data"]

#  create a new dataframe for the table
df_table = pd.DataFrame(columns=['Token', 'Current', 'Prior Week', 'YTD', 'Prior Year', 'Weekly Change', 'YTD Change', 'YoY Change'])

today = datetime.date.today()
day_of_year = today.timetuple().tm_yday

# Loop through the coinIds and create a dataframe for each coin
for index, coin in enumerate(coinIds):
    col = db[coinIds[index]]
    cursor = col.find({}, {"_id":0, "time":1, "eth_value":1})
    # Convert the cursor to a list of dictionaries, then to a dataframe
    li = list(cursor)
    df1 = pd.DataFrame(li)
    df1['date'] = pd.to_datetime(df1["time"], unit="ms")
    current_price = df1['eth_value'].iloc[-1]
    prior_week_price = df1['eth_value'].iloc[-8]
    ytd_price = df1['eth_value'].iloc[-day_of_year]
    prior_year_price = df1['eth_value'].iloc[-366] if len(df1) >= 366 else '-' 
    name = labels[index]

    new_entry = {
        'Token': name,
        'Current': current_price,
        'Prior Week': prior_week_price,
        'YTD': ytd_price,
        'Prior Year': prior_year_price,
        'Weekly Change': ((current_price - prior_week_price)/prior_week_price)*100,
        'YTD Change': ((current_price - ytd_price)/ytd_price)*100,
        'YoY Change': ((current_price - prior_year_price)/prior_year_price)*100 if prior_year_price != '-' else '-'
    }

    df_table.loc[labels[index]] = new_entry

# def format_dynamic_decimal(value):
#     if isinstance(value, (int, float)):
#         # Remove trailing zeros and decimal point if not necessary
#         formatted_value = ("{:.10f}".format(value)).rstrip("0").rstrip(".")
#         return formatted_value
#     else:
#         return value
pd.set_option('display.float_format', lambda x: '%.3f' % x)

def format_dynamic_decimal(value):
    if isinstance(value, (int, float)):
        # Format the float to a fixed number of decimal places without scientific notation
        formatted_value = "{:.10f}".format(value).rstrip("0").rstrip(".")
        return formatted_value
    else:
        return value


def round_to_1(x):
    if isinstance(x, (int, float)):
        return round(x, -int(floor(log10(abs(x)))))
    else:
        return x


format_func = lambda x: round(x, 8) if isinstance(x, (float)) else x

def apply_brackets(val):
    if isinstance(val, (int, float)) and val < 0:
        return f'({abs(val)})'
    elif isinstance(val, (int, float)):
        return f'{val}'
    else:
        return val
    
# df = df_table.applymap(round_to_1).applymap(apply_brackets)
df = df_table.applymap(format_dynamic_decimal).applymap(apply_brackets)
print(df)

def display_bit1_portfolio_table_eth():
    return html.Div([
        html.H6('BIT1 Portfolio (ETH Denominated)', style={'text-align': 'left'}),
        dash_table.DataTable(
            columns=[{"name": i, "id": i} for i in df.columns],
            data=df.to_dict("records"),
            style_cell={'textAlign': 'center'},
            style_data_conditional=[
                {
                    'if': {'column_id': c, 'filter_query': '{{{}}} contains "("'.format(c)},
                    'color': 'red'
                } for c in ['Weekly Change', 'YTD Change', 'YoY Change']
            ],
            style_header={'fontWeight': 'bold'},
        ),
    ])