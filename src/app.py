import dash
import dash_bootstrap_components as dbc
from dash import (
    Dash,
    html,
)

import stores
from components import (
    topbars,
    upload_dialogs,
)
# from utils import echo

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
    topbars.topbar,
    html.Div(
        dash.page_container,
        id="page-content",
    ),
])

topbars.register(app)
upload_dialogs.register(app)

if __name__ == '__main__':
    app.run_server(debug=True)
