import base64
from typing import Tuple

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

ok_btn = dbc.Button('Ok', id='upload-ok-btn', disabled=True)
cancel_btn = dbc.Button('Cancel', id='upload-cancel-btn')
status_label = html.Div(id='upload-status')

_upload_dialog = modals.init_modal(
    id='upload-dialog',
    title='Upload dataset',
    body=[
        dataset_uploader,
        status_label,
    ],
    buttons=[
        ok_btn,
        cancel_btn,
    ]
)

layout = _upload_dialog


def _decode_contents(contents: str) -> Tuple[str, bytes]:
    """returns a tuple of content-type and the decoded data"""
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    return content_type, decoded


def register(app):  # type: ignore

    @app.callback(
        [
            Output(_upload_dialog, 'is_open'),
            Output(status_label, 'children', allow_duplicate=True),
            Output(ok_btn, 'disabled', allow_duplicate=True),
            Output(dataset_uploader, 'contents'),
        ],
        Input(stores.upload_dialog_flag, 'data'),
    )
    def on_upload_dialog_flag(flag: bool) -> Tuple[bool, None, bool, None]:
        """Open/close upload dialog"""
        # XXX: uploader contents must be cleared so that its callback will
        # trigger (due to change) if the same file is reuploaded
        return flag, None, True, None

    @app.callback(
        Output(stores.upload_dialog_flag, 'data', allow_duplicate=True),
        Input(cancel_btn, 'n_clicks'),
    )
    def on_cancel_btn_click(n: int) -> bool:
        """Close upload dialog"""
        return False

    @app.callback(
        [
            Output(stores.uploaded_file, 'data'),
            Output(status_label, 'children', allow_duplicate=True),
            Output(ok_btn, 'disabled'),
        ],
        Input(dataset_uploader, 'contents'),
        State(dataset_uploader, 'filename'),
    )
    def on_dataset_uploaded(
        contents: str,
        filename: str,
    ) -> Tuple[dict, str, bool]:
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
            Output(stores.dataset_id, 'data'),
            Output(stores.upload_dialog_flag, 'data', allow_duplicate=True),
            Output(stores.conf_dialog_flag, 'data', allow_duplicate=True),
        ],
        [
            Input(ok_btn, 'n_clicks'),
            State(stores.uploaded_file, 'data'),
        ],
    )
    def on_ok_btn_click(
        n: int,
        uploaded_file: dict
    ) -> Tuple[Patch, str, bool, int]:
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
            filename,
            False,
            stores.OPEN_FROM_UPLOAD,
        )
