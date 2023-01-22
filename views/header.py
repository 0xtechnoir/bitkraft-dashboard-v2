from dash import html

def display_header():
    return html.Div(
            children=[
                html.H1(
                    children="BITKRAFT Analytics", className="header-title"
                ),
            ],
            className="header",
        )
