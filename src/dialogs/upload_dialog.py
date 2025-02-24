import dash_bootstrap_components as dbc
import pandas as pd
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
from stores import SheetName

from import_utils import (
    decode_contents,
    import_dataset,
    load_dfs,
)

from dialogs.common import register_dialog_flag_callback

_dataset_uploader = dcc.Upload(
    id='upload-data',
    children=html.Div([
        'Drag and drop or ',
        html.A('click to select a dataset'),
    ]),
    accept='.csv,.xlsx',
    multiple=False,
)

_ok_btn = dbc.Button('Ok', id='upload-ok-btn', disabled=True)
_cancel_btn = dbc.Button('Cancel', id='upload-cancel-btn')
_status_label = html.Div(id='upload-status')

_upload_dialog = modals.init_modal(
    id='upload-dialog',
    title='Upload dataset',
    body=[
        _dataset_uploader,
        _status_label,
    ],
    buttons=[
        _ok_btn,
        _cancel_btn,
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


def register(app):  # type: ignore
    register_dialog_flag_callback(app, _upload_dialog,
                                  stores.upload_dialog_flag,
                                  stores.upload_dialog_init)

    @app.callback(
        [
            Output(_status_label, 'children', allow_duplicate=True),
            Output(_ok_btn, 'disabled', allow_duplicate=True),
            Output(_dataset_uploader, 'contents'),
        ],
        Input(stores.upload_dialog_init, 'data'),
    )
    def on_dialog_init(signal: bool) -> tuple[str, bool, None]:
        '''init upload dialog'''
        # XXX: uploader contents must be cleared so that its callback will
        # trigger (due to change) if the same file is reuploaded
        return '', True, None

    @app.callback(
        Output(stores.upload_dialog_flag, 'data', allow_duplicate=True),
        Input(_cancel_btn, 'n_clicks'),
    )
    def on_cancel_btn_click(n: int) -> bool:
        """Close upload dialog"""
        return False

    @app.callback(
        [
            Output(stores.uploaded_name, 'data'),
            Output(stores.uploaded_data, 'data'),
            Output(_status_label, 'children', allow_duplicate=True),
            Output(_ok_btn, 'disabled'),
        ],
        Input(_dataset_uploader, 'contents'),
        State(_dataset_uploader, 'filename'),
    )
    def on_dataset_uploaded(
        contents: str,
        filename: str,
    ) -> tuple[str, str, str, bool]:
        """Store uploaded dataset, and enable ok button"""
        if not contents:
            return no_update
        status = f'{filename} uploaded'
        return filename, contents, status, False

    @app.callback(
        [
            Output(stores.upload_dialog_flag, 'data', allow_duplicate=True),
            Output(_duplicate_dialog, 'is_open', allow_duplicate=True),
            Output(_import_dialog, 'is_open', allow_duplicate=True),
            Output(_import_status_text, 'children', allow_duplicate=True),
        ],
        Input(_ok_btn, 'n_clicks'),
        State(stores.datasets, 'data'),
        State(stores.uploaded_name, 'data'),
    )
    def on_ok_btn_click(
        n: int,
        datasets: dict,
        dataset_id: str
    ) -> tuple[bool, bool, bool, str]:
        '''close upload dialog, open duplicate dialog or import dialog'''
        if dataset_id in datasets:
            return (False, True) + (no_update,)*2  # duplicate
        return False, no_update, True, dataset_id

    @app.callback(
        Output(_duplicate_name_text, 'children'),
        Input(_duplicate_dialog, 'is_open'),
        State(stores.uploaded_name, 'data'),
    )
    def on_duplicate_dialog_open(flag: bool, dataset_id: str) -> str:
        '''init duplicate dialog'''
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
        State(stores.uploaded_name, 'data'),
    )
    def on_duplicate_resolution_btn_click(
        update_clicks: int,
        replace_clicks: int,
        replace_id: str,
        dataset_id: str,
    ) -> tuple[bool, bool, bool, bool, str]:
        '''close duplicate dialog, go through replace confirmation or go
        straight to import dialog'''
        do_replace = (callback_context.triggered_id == replace_id)
        return False, do_replace, do_replace, (not do_replace), dataset_id

    @app.callback(
        [
            Output(_confirm_replace_dialog, 'displayed', allow_duplicate=True),
            Output(_import_dialog, 'is_open', allow_duplicate=True),
        ],
        Input(_confirm_replace_dialog, 'submit_n_clicks'),
        State(stores.uploaded_name, 'data'),
    )
    def on_confirm_replace(n: int, dataset_id: str) -> tuple[bool, bool]:
        '''transitions from replace dialog to import dialog'''
        return False, True

    @app.callback(
        [
            Output(stores.dataset_id, 'data', allow_duplicate=True),
            Output(stores.datasets, 'data'),
            Output(stores.dataset_data, 'data'),
            Output(stores.validations, 'data', allow_duplicate=True),
            Output(stores.validation_reports, 'data', allow_duplicate=True),
            Output(stores.validation_summaries, 'data', allow_duplicate=True),
            Output(_import_dialog, 'is_open', allow_duplicate=True),
            Output(stores.conf_dialog_flag, 'data', allow_duplicate=True),
            Output('url', 'pathname', allow_duplicate=True),
        ],
        Input(_import_dialog, 'is_open'),
        State(stores.uploaded_name, 'data'),
        State(stores.uploaded_data, 'data'),
        State(stores.replace_on_dup, 'data'),
        State(stores.datasets, 'data'),
    )
    def on_import(
        flag: bool,
        filename: str,
        contents: str,
        replace_on_dup: bool,
        datasets: dict,
    ) -> tuple[str, Patch, Patch, Patch, Patch, Patch, bool, int, str]:
        """import dataset, close import dialog, open conf dialog or go to
        dataset page directly"""
        # TODO:
        # - error handling around import_dataset
        # - validate file type
        if not flag:
            return no_update
        (_, data) = decode_contents(contents)
        dataset_id = filename
        is_dup = dataset_id in datasets

        dfs: dict[SheetName, pd.DataFrame] = load_dfs(filename, data)
        ds = import_dataset(dataset_id, dfs)

        if is_dup and (not replace_on_dup):
            prev_ds = datasets[dataset_id]
            ds['revision'] = prev_ds['revision'] + 1

        # patches
        dataset_patch = Patch()
        dataset_patch[dataset_id] = ds
        dataset_data_patch = Patch()
        dataset_data_patch[dataset_id] = stores._encode_dataframes(dfs)
        validation_patch = Patch()
        validation_patch[dataset_id] = {}

        # same validation patch can be used on validation reports/summaries as
        # well, since they're all indexed by dataset_id
        replace_val = (is_dup and replace_on_dup)
        val_update = validation_patch if replace_val else no_update

        conf_flag = no_update if is_dup else stores.OPEN_FROM_UPLOAD
        url = utils.get_dataset_path(filename) if is_dup else no_update
        return (
            dataset_id,
            dataset_patch,
            dataset_data_patch,
            val_update,
            val_update,
            val_update,
            False,
            conf_flag,
            url,
        )
