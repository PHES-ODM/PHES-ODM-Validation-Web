from typing import Dict, List, Tuple
from enum import Enum
# from pprint import pprint

import dash_bootstrap_components as dbc
import orjson as json
import pandas as pd
import yaml
from dash import (
    Input,
    Output,
    State,
    dash_table,
    dcc,
    html,
)
from dash.dash import no_update
from dash.development.base_component import Component
from odm_validation.reports import ErrorKind

import stores
import utils
from components import modals

Format = Enum('Format', type=str, names=['CSV', 'JSON', 'YAML'])

_error_level_names = list(map(lambda x: x.name, ErrorKind))
_format_names = list(map(lambda x: x.name, Format))

_content = html.Div()
_format = dcc.Dropdown(_format_names, Format.CSV.name, clearable=False)
_error_level = dcc.Dropdown(_error_level_names, ErrorKind.WARNING.name,
                            clearable=False)
_download_btn = dbc.Button('Download', id='download-btn')
_close_btn = dbc.Button('Close', id='close-btn')
_downloader = dcc.Download()

layout = modals.init_modal(
    id='report-dialog',
    title='Validation Report',
    body=[
        _content,
        'Format',
        _format,
        'Error Level',
        _error_level,
        _downloader,
    ],
    buttons=[
        _download_btn,
        _close_btn,
    ],
    class_name='report-modal',
)


def errorLevel(e: dict) -> ErrorKind:
    result = ErrorKind.ERROR
    if 'errorType' not in e:
        result = ErrorKind.WARNING
    return result


def errorToRow(e: dict) -> dict:
    return {
        'errorLevel': errorLevel(e).name,
        'table': e['tableName'],
        'column': str(e['columnName']),
        'row': str((e.get('rowNumber', None) or e.get('rowNumbers'))),
        'rule_id': str(e.get('errorType', None) or e.get('warningType')),
        'message': e['message'],
    }


def errorToRowPreview(e: dict) -> dict:
    row = errorToRow(e)
    del row['errorLevel']
    return row


def fmttable(errors: List[dict]) -> List[dict]:
    return list(map(errorToRowPreview, errors))


def error_kind_key(kind: ErrorKind) -> str:
    '''ERROR -> errors, etc.'''
    return kind.name.lower() + 's'


def reportToCsvStr(report: dict) -> str:
    rows: List[Dict] = []
    for kind in reversed(ErrorKind):
        errors = report.get(error_kind_key(kind), [])
        rows += map(errorToRow, errors)
    df = pd.DataFrame(rows)
    return df.to_csv(index=False)


def register(app):  # type: ignore

    @app.callback(
        [
            Output(layout, 'is_open'),
            Output(stores.report_dialog_init, 'data'),
            Output(_content, 'children', allow_duplicate=True),
        ],
        Input(stores.report_dialog_flag, 'data'),
    )
    def on_report_dialog_flag(flag: bool) -> Tuple[bool, bool, str]:
        """Open/close dialog"""
        if not flag:
            return (flag, no_update, no_update)
        return (flag, True, 'Loading...')

    # TODO: optimize using client callback due to transfer of big reports
    @app.callback(
        Output(_content, 'children', allow_duplicate=True),
        Input(stores.report_dialog_init, 'data'),
        State('url', 'pathname'),
        State(stores.validation_reports, 'data'),
    )
    def on_report_dialog_init(flag: bool, pathname: str, reports: dict
                              ) -> Component:
        """init dialog"""
        # XXX: dialog init requires separate store/signal to avoid
        # re-transferring state-input when closing the dialog.
        (dataset_id, validation_name) = utils.get_validation_id(pathname)
        report = reports[dataset_id][validation_name]
        errors = report['errors']
        rows = fmttable(errors)
        table = dash_table.DataTable(
            rows,
            fixed_rows={'headers': True},
            page_size=100,
            style_cell={
                'minWidth': 30,
                'textAlign': 'left',
            },
            style_cell_conditional=[
                {
                    'if': {'column_id': 'row'},
                    'textAlign': 'right',
                }
            ],
        )
        return table

    @app.callback(
        Output(stores.report_dialog_flag, 'data', allow_duplicate=True),
        Input(_close_btn, 'n_clicks'),
    )
    def on_close_btn_click(n: int) -> bool:
        """Close dialog"""
        return False

    @app.callback(
        Output(_downloader, 'data'),
        Input(_download_btn, 'n_clicks'),
        State('url', 'pathname'),
        State(stores.validations, 'data'),
        State(stores.validation_reports, 'data'),
        State(_format, 'value'),
        State(_error_level, 'value'),
        prevent_initial_call=True,
    )
    def on_download_btn_click(n: int, pathname: str,
                              validations: dict, reports: dict,
                              fmt_name: str, error_level: str) -> dict:
        if not n:
            return no_update
        fmt = Format[fmt_name]
        ext = fmt_name.lower()
        (dataset_id, validation_name) = utils.get_validation_id(pathname)
        v = validations[dataset_id][validation_name]
        ds_rev = v['ds_revision']
        report = reports[dataset_id][validation_name]

        # del metadata
        metadata_keys = [
            'validationRuleFields',
            'row',
            'rows',
            'coercionRules',
        ]
        for kind in ErrorKind:
            errors = report[error_kind_key(kind)]
            for e in errors:
                for key in metadata_keys:
                    e.pop(key, None)

        # del excluded error levels
        min_error_lvl = ErrorKind[error_level]
        for kind in ErrorKind:
            if kind == min_error_lvl:
                break
            report.pop(error_kind_key(kind), None)

        # XXX: orjson.dumps -> bytes
        out_data = ''
        if fmt == Format.JSON:
            out_data = json.dumps(report).decode()
        elif fmt == Format.YAML:
            out_data = yaml.dump(report, sort_keys=False)
        elif fmt == Format.CSV:
            out_data = reportToCsvStr(report)

        filename = f'{dataset_id}-{ds_rev}-{validation_name}.{ext}'
        return dict(content=out_data, filename=filename)
