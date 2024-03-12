import logging
from typing import Callable, Tuple
# from pprint import pprint

import dash_bootstrap_components as dbc
import orjson as json
from dash import (
    Input,
    Output,
    Patch,
    State,
    dcc,
    html,
    no_update,
)
from dash.development.base_component import Component
from odm_validation.input_data import DataKind
from odm_validation.reports import ErrorVerbosity
from odm_validation.summarization import SummaryKey, summarize_report
from odm_validation.validation import _validate_data_ext

import stores
import utils
from odm import odm
from components import modals
from stores import ValidationSetup

cancel_btn = dbc.Button('Cancel')
close_btn = dbc.Button('Close', disabled=True)
progress_text = html.P(id='progress-text')
result_text = html.P(id='result-text')
dataset_name_text = html.Strong(id='dataset-name-text')
table_name_text = html.P(id='table-name-text')
progress_bar = html.Progress(id='progress-bar')

confirm_cancel_dialog = dcc.ConfirmDialog(
    message='Are you sure you want to cancel the validation process?')

_validation_progress_dialog = modals.init_modal(
    id='validation-progress-dialog',
    title='Validating',
    body=[
        confirm_cancel_dialog,
        dataset_name_text,
        table_name_text,
        progress_bar,
        result_text,
    ],
    buttons=[
        close_btn,
        cancel_btn,
    ]
)

layout = _validation_progress_dialog


def map_table_data(sheets: dict, mapping: dict) -> dict:
    '''maps `sheets` to ODM tables, using `mapping`'''
    tables = {}
    for sheet_name, data in sheets.items():
        table_name = mapping[sheet_name]
        if not table_name:
            continue
        tables[table_name] = data
    return tables


def unpack_setup(vs: ValidationSetup) -> Tuple[str, str, str]:
    return vs['dataset_id'], vs['validation_name'], vs['profile_id']


def register(app):  # type: ignore

    @app.callback(
        [
            Output(layout, 'is_open'),
            Output(dataset_name_text, 'children', allow_duplicate=True),
            Output(table_name_text, 'children', allow_duplicate=True),
            Output(result_text, 'children', allow_duplicate=True),
            Output(progress_bar, 'value', allow_duplicate=True),
            Output(stores.validation_trigger, 'data'),
            Output(stores.cancel_operation, 'data'),
        ],
        Input(stores.progress_dialog_flag, 'data'),
        State(stores.validation_setup, 'data'),
    )
    def on_dialog_flag(flag: bool, setup: ValidationSetup
                       ) -> Tuple[bool, str, str, str, str, bool, bool]:
        '''Open/close dialog. When opening: initialize dialog, and start
        validation. This is separate from on_validation since it needs to
        initialize the dialog before starting the blocking validation
        process.'''
        if not flag:
            return (flag,) + (no_update,)*6
        dataset_id, _, _ = unpack_setup(setup)
        return flag, dataset_id, '', '', '0', True, False

    @app.callback(
        output=[
            Output(table_name_text, 'children'),
            Output(result_text, 'children'),
            Output(stores.validations, 'data'),
        ],
        inputs=[
            Input(stores.validation_trigger, 'data'),
            State(stores.datasets, 'data'),
            State(stores.validation_setup, 'data'),
        ],
        background=True,
        running=[
            (Output(close_btn, 'disabled'), True, False),
            (Output(cancel_btn, 'disabled'), False, True),
            (Output(progress_bar, 'hidden'), False, True),
        ],
        cancel=Input(stores.cancel_operation, 'data'),
        progress=[
            Output(table_name_text, 'children'),
            Output(progress_bar, 'value'),
            Output(progress_bar, 'max'),
        ],
        manager=stores.background_callback_manager,
        prevent_initial_call=True,
    )
    def on_validation(
        set_progress: Callable,
        trigger: bool,
        datasets: dict,
        setup: ValidationSetup,
    ) -> Tuple[Component, Component, Patch]:
        '''open/close dialog, start validation when opening, show report'''
        if not trigger:
            return no_update
        dataset_id, validation_name, profile_id = unpack_setup(setup)
        assert dataset_id in datasets, f'unknown dataset {dataset_id}'
        ds = datasets[dataset_id]
        version = odm.Version(ds['odm_version'])
        sheets, mapping = (ds['sheets'], ds['table_mapping'])
        tables = map_table_data(sheets, mapping)
        schema = odm.load_schema(version)

        def on_progress(action: str, table_id: str, current: int, total: int
                        ) -> None:
            # per table
            set_progress((table_id, str(current), str(total)))

        logging.info(f'running validation "{validation_name}" ' +
                     f'of "{dataset_id}" with "{profile_id}"')

        report = _validate_data_ext(schema=schema,
                                    data=tables,
                                    data_kind=DataKind.spreadsheet,
                                    data_version=version.value,
                                    on_progress=on_progress,
                                    verbosity=ErrorVerbosity.MESSAGE)

        es = report.errors
        ws = report.warnings
        keys = {SummaryKey.TABLE, SummaryKey.COLUMN, SummaryKey.ROW}
        report_summary = summarize_report(report, by=keys)

        summary = [
            html.P('Validation complete'),
            html.P(f'errors: {len(es)}, warnings: {len(ws)}'),
        ]

        validation = Patch()
        validation[dataset_id][validation_name] = stores.Validation(
            name=validation_name,
            summary='',
            report=json.dumps(report.__dict__),
            report_summary=report_summary.toJson(),
            ds_revision=ds['revision'],
        )
        return '', summary, validation

    @app.callback(
        Output(confirm_cancel_dialog, 'displayed', allow_duplicate=True),
        Input(cancel_btn, 'n_clicks'),
    )
    def on_cancel_btn_click(n: int) -> bool:
        return True

    @app.callback(
        [
            Output(stores.cancel_operation, 'data', allow_duplicate=True),
            Output(table_name_text, 'children', allow_duplicate=True),
            Output(result_text, 'children', allow_duplicate=True),
        ],
        Input(confirm_cancel_dialog, 'submit_n_clicks'),
    )
    def on_confirm_cancel_click(n: int) -> Tuple[bool, Component, Component]:
        text = html.P('Validation canceled')
        return True, '', text

    @app.callback(
        [
            Output(stores.progress_dialog_flag, 'data', allow_duplicate=True),
            Output('url', 'pathname', allow_duplicate=True),
        ],
        Input(close_btn, 'n_clicks'),
        State(stores.validation_setup, 'data'),
        State(stores.cancel_operation, 'data'),
    )
    def on_close_btn_click(
        n: int,
        setup: ValidationSetup,
        canceled: bool,
    ) -> Tuple[bool, str]:
        '''close dialog, go to validation page'''
        if canceled:
            return False, no_update
        dataset_id, validation_name, _ = unpack_setup(setup)
        path = utils.get_validation_path(dataset_id, validation_name)
        return (
            False,
            path,
        )
