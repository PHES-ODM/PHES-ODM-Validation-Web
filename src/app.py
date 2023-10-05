import logging

import dash
import dash_bootstrap_components as dbc
from dash import (
    Dash,
    dcc,
    html,
)

import stores
from components import (
    dataset_infos,
    topbars,
    upload_dialogs,
)


logging.basicConfig(level=logging.INFO)

stylesheets = [
    dbc.themes.BOOTSTRAP,
    'https://codepen.io/chriddyp/pen/bWLwgP.css'
]

app = Dash(__name__, use_pages=True, external_stylesheets=stylesheets,
           prevent_initial_callbacks=True)


app.layout = html.Div([
    # stores
    stores.conf_dialog_flag,
    stores.datasets,
    stores.upload_dialog_flag,
    stores.uploaded_file,

    # dialogs
    upload_dialogs.upload_dialog,

    # page
    dcc.Location(id='url', refresh='callback-nav'),
    topbars.topbar,
    html.Div(
        dash.page_container,
        id="page-content",
    ),
])

topbars.register(app)
upload_dialogs.register(app)
dataset_infos.register(app)


if __name__ == '__main__':
    app.run_server(debug=True)
