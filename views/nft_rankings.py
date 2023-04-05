import pandas as pd
from dash import html, dash_table
import pymongo
import pandas as pd
import os
import datetime
from dotenv import load_dotenv
from math import log10, floor

load_dotenv()
MONGODB_CONNECTION = os.getenv('MONGODB_CONNECTION')
client = pymongo.MongoClient(MONGODB_CONNECTION)
db = client["historical_price_data"]
col = db['nft_collection_ranking']

pd.set_option('display.float_format', '{:,.2f}'.format)

column_names = [
    "name", 
    "volume_usd", 
    "market_cap_usd", 
    "floor_price_eth", 
    "floor_price_usd", 
    "holder_num", 
    "contracts", 
    "num_contracts",
    "floor_change_24hr",
    "floor_change_7d",
    "floor_change_30d"
]

df = pd.DataFrame(columns=column_names)

sorted_records = col.find().sort("Rank", 1)

# for record in sorted_records:
#     print(record)

for record in sorted_records:

    new_row = pd.DataFrame([{
        'name': record['name'],
        'volume_usd': record['volume_usd'],
        "market_cap_usd": record['market_cap_usd'],
        "floor_price_eth": record['floor_price_eth'],
        "floor_price_usd": record['floor_price_usd'],
        "holder_num": record['holder_num'],
        "floor_change_24hr": record['floor_change_24hr'],
        "floor_change_7d": record['floor_change_7d'],
        "floor_change_30d": record['floor_change_30d']
    }], columns=column_names)

    df = pd.concat([df, new_row], ignore_index=True)

print(df)

