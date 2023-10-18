import base64
from urllib.parse import quote

import dash_bootstrap_components as dbc
from dash import (
    Input,
    Output,
    Patch,
    State,
    dcc,
    html,
)
from dash.dash import no_update

import stores
from components import modals
from dataset_import import import_dataset

dataset_uploader = dcc.Upload(
    id='upload-data',
    children=html.Div([
        'Drag and drop or ',
        html.A('click to select a dataset'),
    ]),
    accept='.csv,.xlsx',
    multiple=False,
)

upload_ok_btn = dbc.Button('Ok', id='upload-ok-btn', disabled=True)
upload_cancel_btn = dbc.Button('Cancel', id='upload-cancel-btn')
upload_status = html.Div(id='upload-status')

upload_dialog = modals.init_modal(
    id='upload-dialog',
    title='Upload dataset',
    body=[
        dataset_uploader,
        upload_status,
    ],
    buttons=[
        upload_ok_btn,
        upload_cancel_btn,
    ]
)


def _decode_contents(contents):
    """returns a tuple of content-type and the decoded data"""
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    return content_type, decoded


def register(app):

    @app.callback(
        [
            Output(upload_dialog, 'is_open'),
            Output(upload_status, 'children', allow_duplicate=True),
            Output(upload_ok_btn, 'disabled', allow_duplicate=True),
            Output(dataset_uploader, 'contents'),
        ],
        Input(stores.upload_dialog_flag, 'data'),
    )
    def on_upload_dialog_flag(flag):
        """Open/close upload dialog"""
        # XXX: uploader contents must be cleared so that its callback will
        # trigger (due to change) if the same file is reuploaded
        return flag, None, True, None

    @app.callback(
        Output(stores.upload_dialog_flag, 'data', allow_duplicate=True),
        Input(upload_cancel_btn, 'n_clicks'),
    )
    def on_upload_cancel_btn(n):
        """Close upload dialog"""
        return False

    @app.callback(
        [
            Output(stores.uploaded_file, 'data'),
            Output(upload_status, 'children', allow_duplicate=True),
            Output(upload_ok_btn, 'disabled'),
        ],
        [
            Input(dataset_uploader, 'contents'),
            State(dataset_uploader, 'filename'),
        ],
    )
    def on_dataset_uploaded(contents, filename):
        """Store uploaded dataset, and enable ok button"""
        if not contents:
            return no_update
        uploaded_file = {
            'filename': filename,
            'contents': contents,
        }
        status = f'{filename} uploaded'
        return uploaded_file, status, False

    @app.callback(
        [
            Output(stores.datasets, 'data'),
            Output(stores.upload_dialog_flag, 'data', allow_duplicate=True),
            Output('url', 'pathname'),
            Output('url', 'search'),
        ],
        [
            Input(upload_ok_btn, 'n_clicks'),
            State(stores.uploaded_file, 'data'),
        ],
    )
    def on_upload_ok_btn(n, uploaded_file):
        """Append uploaded dataset, close upload dialog, open conf dialog"""
        # TODO: error handling around import_dataset
        filename = uploaded_file['filename']
        contents = uploaded_file['contents']
        (_, data) = _decode_contents(contents)
        ds = import_dataset(filename, data)
        dataset_patch = Patch()
        dataset_patch[filename] = ds
        return (
            dataset_patch,
            False,
            '/datasets',
            f'?dataset-id={quote(filename)}',
        )
