from maindash import app
from dash.dependencies import Input, Output
from dash import dcc, html, dash_table
import pymongo
import pandas as pd
import plotly.express as px 
import datetime as dt
import plotly.graph_objects as go
import os
import datetime
from dotenv import load_dotenv

def color_negative_red(x):
    if isinstance(x, (int, float)):
        if x < 0:
            color = 'red'
        else:
            color = 'black'
        return f'<span style="color:{color}">{x}</span>'

def highlight_max(cell):
    if isinstance(cell, (int, float)) and cell < 0 :
        return 'color: red'
    else:
        return 'color: black'
    
# def highlight_max(s):
#     if s.dtype == np.object:
#         is_neg = [False for _ in range(s.shape[0])]
#     else:
#         is_neg = s < 0
#     return ['color: red;' if cell else 'color:black' 
#             for cell in is_neg]

def format_cell(x):
    # first check is the value is a number
    if isinstance(x, (int, float)):
        # if the value is negative, wrap it in parentheses
        val = round(x, 2)
        print(val)
        if val < 0: 
              
            val = f'({abs(val)})'
            return val
        else:
            return val

    return x

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
    cursor = col.find({}, {"_id":0, "time":1, "usd_value":1})
    # Convert the cursor to a list of dictionaries, then to a dataframe
    li = list(cursor)
    df1 = pd.DataFrame(li)
    df1['date'] = pd.to_datetime(df1["time"], unit="ms")
    # print(df1)
    current_price = df1['usd_value'].iloc[-1]
    prior_week_price = df1['usd_value'].iloc[-8]
    ytd_price = df1['usd_value'].iloc[-day_of_year]
    prior_year_price = df1['usd_value'].iloc[-366] if len(df1) >= 366 else '-'     

    new_entry = {
        'Token': labels[index],
        'Current': current_price,
        'Prior Week': prior_week_price,
        'YTD': ytd_price,
        'Prior Year': prior_year_price,
        'Weekly Change': ((current_price - prior_week_price)/prior_week_price)*100,
        'YTD Change': ((current_price - ytd_price)/ytd_price)*100,
        'YoY Change': ((current_price - prior_year_price)/prior_year_price)*100 if prior_year_price != '-' else '-'
    }

    df_table.loc[labels[index]] = new_entry


# Colour negative cells red
# df_table.style.applymap(color_negative_red, subset=['Weekly Change', 'YTD Change', 'YoY Change'])

format_func = lambda x: "{:.2f}".format(x) if isinstance(x, (int, float)) else x
abs_func = lambda x: f'({abs(x)})' if isinstance(x, (int, float)) and x<0 else x
# df = df_table.style.apply(highlight_max)\
print("1: ", df_table)
df = df_table.style.applymap(color_negative_red)
# df1 = df.applymap(format_cell)
# df = df_table.applymap(format_func).applymap(abs_func)
print("2: ", df)

# df1 = df.applymap(abs_func)


def display_bit1_portfolio_table_usd():


    return html.Div(children=[
        dash_table.DataTable(
            df.to_dict('records'),
            [{"name": i, "id": i} for i in df.columns],
        ),
    ])