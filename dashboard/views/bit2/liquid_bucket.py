from maindash import app
from utilities.read_google_sheets import read_google_sheet
from dash import html, dash_table
from dash.dash_table import DataTable
import pandas as pd

#  create a new dataframe for the table
df_table = pd.DataFrame(
    columns=['Token', 'Cost ($)', 'FMV ($)', '% Change', 'Price at Cost ($)', 'To be Allocated'])

# Pull liquid token data
sheetId = '1wm5Whcdxm7FDBsNeQsJqXtPXJ7tDf6JrjY3EDBlQZPU'
cellRange = 'Market Report!A19:F24'
sheet_values = read_google_sheet(sheetId, cellRange)
if sheet_values:
    sheet_headers = sheet_values[0]
    sheet_data = sheet_values[1:]
    sheet_df = pd.DataFrame(sheet_data, columns=sheet_headers)
else:
    sheet_df = pd.DataFrame()
    
for index, row in sheet_df.iterrows():
    name = row['Token']
    cost = int(row['Cost ($)'])
    fmv = int(row['FMV ($)'])
    perc_change = float(row['% Change'])
    # Directly format "% Change" with or without brackets based on its sign
    perc_change_str = f"({abs(perc_change):.2f}%)" if perc_change < 0 else f"{perc_change:.2f}%"
    price_at_cost = f"{float(row['Price at Cost ($)']):,.3f}" if row['Price at Cost ($)'] else ''
    to_be_allocated = f"{int(row['To be Allocated']):,}" if row['To be Allocated'] else ''
    new_entry = {
        'Token': name,
        'Cost ($)': f"{cost:,}",
        'FMV ($)': f"{fmv:,}",
        '% Change': perc_change_str,
        'Price at Cost ($)': price_at_cost,
        'To be Allocated': to_be_allocated
    }
    df_table = pd.concat([df_table, pd.DataFrame([new_entry])], ignore_index=True)

def display_10m_liquid_bucket():
    return html.Div([
        html.H4('$10m Liquid Bucket', style={'text-align': 'left'}),
        dash_table.DataTable(
            columns=[{"name": i, "id": i} for i in df_table.columns],
            style_table={'width': '100%'},
            data=df_table.to_dict("records"),
            style_cell={
                'textAlign': 'center',
                'padding': '0px 15px',
                'fontSize': '20px',
            },
            style_cell_conditional=[
                {'if': {'column_id': 'Token'}, 'textAlign': 'left'},
            ],
            style_data_conditional=
            [
                {
                    'if': {'column_id': c, 'filter_query': '{{{}}} contains "("'.format(c)},
                    'color': 'red'
                } for c in df_table.columns
            ] + 
            [
                {
                    'if': {
                        'filter_query': '{Token} = \'Total Invested\' || {Token} = \'Total Liquid Allocation\'',
                    },
                    'backgroundColor': '#e8f4ff'}
            ] + [
                {
                    'if': {
                        'column_id': '% Change',
                        'filter_query': '{% Change} contains "("',
                    },
                    'color': 'red',
                },
            ],
            style_header={
                'fontWeight': 'bold',
                'backgroundColor': '#46637f',
                'color': 'white',
            },
        ),
    ], style={'margin': '20px'})
