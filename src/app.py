import dash
import dash_bootstrap_components as dbc
from dash import (
    Dash,
    html,
)

import components as comp

stylesheets = [
    dbc.themes.BOOTSTRAP,
    'https://codepen.io/chriddyp/pen/bWLwgP.css'
]

app = Dash(__name__, use_pages=True, external_stylesheets=stylesheets,
           prevent_initial_callbacks=True)


app.layout = html.Div([
    comp.topbar,
    comp.sidebar,
    html.Div(
        dash.page_container,
        id="page-content",
    ),
])


if __name__ == '__main__':
    app.run_server(debug=True)
