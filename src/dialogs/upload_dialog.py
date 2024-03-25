import base64
from typing import Dict, Tuple

import dash_bootstrap_components as dbc
from dash import (
    Input,
    Output,
    Patch,
    State,
    callback_context,
    dcc,
    html,
)
from dash.dash import no_update

import stores
import utils
from components import modals
from dataset_import import SheetName, TableData, import_dataset, load_sheets

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

_update_btn = dbc.Button('Update', id='update-btn')
_replace_btn = dbc.Button('Replace', id='replace-btn')

_duplicate_name_text = html.Span()

_duplicate_dialog = modals.init_modal(
    id='duplicate-dialog',
    title='Duplicate dataset',
    body=[
        html.Div([
            html.P([
                '''Another dataset with the name "''',
                _duplicate_name_text,
                '''" is already uploaded. Two datasets with the same name is
                currently not allowed. You can either: '''
            ]),
            html.Strong('1. Update the existing dataset'),
            html.P(
                '''This updates the current dataset in the tool with the new
                one. You won't lose any validations attached to the existing
                dataset, they will be moved over.'''
            ),
            html.Strong('2. Replace the existing dataset'),
            html.P(
                '''This will delete the old dataset and any validations
                associated with it, replacing it with the new one. What do you
                want to do?'''
            ),
        ]),
    ],
    buttons=[
        _update_btn,
        _replace_btn,
    ]
)

_confirm_replace_dialog = dcc.ConfirmDialog(
    id='confirm-replace-dialog',
    message='Are you sure you want to replace the existing dataset? You ' +
            'will lose all data associated with it, including any validations.'
)

_import_status_text = html.Strong()

_import_dialog = modals.init_modal(
    id='import-dialog',
    title='Importing dataset...',
    body=[
        html.Div(
            _import_status_text,
        ),
        html.Div(
            html.Progress()
        ),
    ],
    buttons=[],
)

layout = html.Div([
    _upload_dialog,
    _duplicate_dialog,
    _confirm_replace_dialog,
    _import_dialog,
])


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
            Output(stores.upload_dialog_flag, 'data', allow_duplicate=True),
            Output(_duplicate_dialog, 'is_open', allow_duplicate=True),
            Output(_import_dialog, 'is_open', allow_duplicate=True),
            Output(_import_status_text, 'children', allow_duplicate=True),
        ],
        Input(ok_btn, 'n_clicks'),
        State(stores.datasets, 'data'),
        State(stores.uploaded_file, 'data'),
    )
    def on_ok_btn_click(
        n: int,
        datasets: dict,
        uploaded_file: dict
    ) -> Tuple[bool, bool, bool, str]:
        '''close upload dialog, open duplicate dialog or import dialog'''
        dataset_id = uploaded_file['filename']
        if dataset_id in datasets:
            return (False, True) + (no_update,)*2  # duplicate
        return False, no_update, True, dataset_id

    @app.callback(
        Output(_duplicate_name_text, 'children'),
        Input(_duplicate_dialog, 'is_open'),
        State(stores.uploaded_file, 'data'),
    )
    def on_duplicate_dialog_open(flag: bool, uploaded_file: dict) -> str:
        '''init duplicate dialog'''
        dataset_id = uploaded_file['filename']
        if not flag:
            return no_update
        return dataset_id

    # breaking the "1 input per callback" rule here for simplicity
    @app.callback(
        [
            Output(_duplicate_dialog, 'is_open', allow_duplicate=True),
            Output(stores.replace_on_dup, 'data', allow_duplicate=True),
            Output(_confirm_replace_dialog, 'displayed', allow_duplicate=True),
            Output(_import_dialog, 'is_open', allow_duplicate=True),
            Output(_import_status_text, 'children', allow_duplicate=True),
        ],
        Input(_update_btn, 'n_clicks'),
        Input(_replace_btn, 'n_clicks'),
        State(_replace_btn, 'id'),
        State(stores.uploaded_file, 'data'),
    )
    def on_duplicate_resolution_btn_click(
        update_clicks: int,
        replace_clicks: int,
        replace_id: str,
        uploaded_file: dict,
    ) -> Tuple[bool, bool, bool, bool, str]:
        '''close duplicate dialog, go through replace confirmation or go
        straight to import dialog'''
        do_replace = (callback_context.triggered_id == replace_id)
        dataset_id = uploaded_file['filename']
        return False, do_replace, do_replace, (not do_replace), dataset_id

    @app.callback(
        [
            Output(_confirm_replace_dialog, 'displayed', allow_duplicate=True),
            Output(_import_dialog, 'is_open', allow_duplicate=True),
        ],
        Input(_confirm_replace_dialog, 'submit_n_clicks'),
        State(stores.uploaded_file, 'data'),
    )
    def on_confirm_replace(n: int, uploaded_file: dict) -> Tuple[bool, bool]:
        return False, True

    @app.callback(
        [
            Output(stores.dataset_id, 'data', allow_duplicate=True),
            Output(stores.datasets, 'data'),
            Output(stores.dataset_sheets, 'data'),
            Output(stores.validations, 'data', allow_duplicate=True),
            Output(_import_dialog, 'is_open', allow_duplicate=True),
            Output(stores.conf_dialog_flag, 'data', allow_duplicate=True),
            Output('url', 'pathname', allow_duplicate=True),
        ],
        Input(_import_dialog, 'is_open'),
        State(stores.uploaded_file, 'data'),
        State(stores.replace_on_dup, 'data'),
        State(stores.datasets, 'data'),
    )
    def on_import(
        flag: bool,
        uploaded_file: dict,
        replace_on_dup: bool,
        datasets: dict,
    ) -> Tuple[str, Patch, Patch, Patch, bool, bool, str]:
        """import dataset, close import dialog, open conf dialog or go to
        dataset page directly"""
        # TODO: error handling around import_dataset
        if not flag:
            return no_update
        filename = uploaded_file['filename']
        contents = uploaded_file['contents']
        (_, data) = _decode_contents(contents)
        dataset_id = filename
        is_dup = dataset_id in datasets

        sheets: Dict[SheetName, TableData] = load_sheets(filename, data)
        ds = import_dataset(dataset_id, sheets)

        if is_dup and (not replace_on_dup):
            prev_ds = datasets[dataset_id]
            ds['revision'] = prev_ds['revision'] + 1

        # patches
        dataset_patch = Patch()
        dataset_patch[dataset_id] = ds
        dataset_sheet_patch = Patch()
        dataset_sheet_patch[dataset_id] = sheets
        validations_patch = Patch()
        validations_patch[dataset_id] = {}

        conf_flag = no_update if is_dup else stores.OPEN_FROM_UPLOAD
        url = utils.get_dataset_path(filename) if is_dup else no_update
        return (
            dataset_id,
            dataset_patch,
            dataset_sheet_patch,
            (validations_patch if (is_dup and replace_on_dup) else no_update),
            False,
            conf_flag,
            url,
        )
