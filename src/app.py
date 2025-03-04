import sys
import logging
from os.path import dirname, join

import dash
import dash_bootstrap_components as dbc
from dash import (
    Dash,
    dcc,
    html,
)

import stores
from components import (
    sidebar,
    topbar,
)
from dialogs import (
    conf_dialog,
    report_dialog,
    share_dialog,
    upload_dialog,
    validation_setup_dialog,
    validation_progress_dialog,
)
from odm import odm_schemas

logging.basicConfig(level=logging.INFO)

odm_schemas.init()

stylesheets = [
    dbc.themes.BOOTSTRAP,
    'https://codepen.io/chriddyp/pen/bWLwgP.css'
]

is_bundle = getattr(sys, "frozen", False)
src_dir = join(dirname(sys.executable), 'src') if is_bundle else ''

app = Dash(__name__, use_pages=True,
           assets_folder=join(src_dir, 'assets'),
           pages_folder=join(src_dir, 'pages'),
           external_stylesheets=stylesheets,
           prevent_initial_callbacks=True,
           compress=True)

app.layout = html.Div([
    # stores
    stores.cancel_operation,
    stores.conf_dialog_flag,
    stores.conf_dialog_init,
    stores.dataset_conf_form,
    stores.dataset_data,
    stores.dataset_id,
    stores.datasets,
    stores.progress_dialog_flag,
    stores.progress_dialog_init,
    stores.replace_on_dup,
    stores.report_dialog_flag,
    stores.report_dialog_init,
    stores.share_dialog_flag,
    stores.share_dialog_init,
    stores.share_dialog_share,
    stores.sharing_schema_data,
    stores.sharing_schema_filename,
    stores.upload_dialog_flag,
    stores.upload_dialog_init,
    stores.uploaded_data,
    stores.uploaded_name,
    stores.validation_dialog_flag,
    stores.validation_dialog_init,
    stores.validation_setup,
    stores.validation_trigger,
    stores.validation_reports,
    stores.validation_summaries,
    stores.validations,

    # dialogs
    conf_dialog.layout,
    report_dialog.layout,
    share_dialog.layout,
    upload_dialog.layout,
    validation_setup_dialog.layout,
    validation_progress_dialog.layout,

    # page
    dcc.Location(id='url', refresh='callback-nav'),
    topbar.layout,
    html.Div(
        dash.page_container,
        id="page-content",
    ),
])

# register component/dialog callbacks
conf_dialog.register(app)  # type: ignore
report_dialog.register(app)  # type: ignore
share_dialog.register(app)  # type: ignore
sidebar.register(app)  # type: ignore
topbar.register(app)  # type: ignore
upload_dialog.register(app)  # type: ignore
validation_setup_dialog.register(app)  # type: ignore
validation_progress_dialog.register(app)  # type: ignore

# Flask app instance, needed by Gunicorn and specified on command-line
# eg. gunicorn -b 127.0.0.1:8000 app:server
server = app.server

if __name__ == '__main__':
    app.run_server(debug=True)
