from dash import html
from maindash import app
from views.display_charts import display_charts
from views.header import display_header
from views.menu import display_menu
from maindash import data

app.title = "Avocado Analytics: Understand Your Avocados!"
server = app.server

app.layout = html.Div(
    children=[
        display_header(),
        display_menu(),
        display_charts()
    ]
)

if __name__ == "__main__":
    app.run_server(debug=True)