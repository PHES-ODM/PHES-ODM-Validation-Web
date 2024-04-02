from typing import List, Tuple

import dash_bootstrap_components as dbc
import dash.dcc as dcc
from dash import (
    ALL,
    Input,
    Output,
    Patch,
    State,
    callback_context,
    html,
    no_update,
)
from dash.development.base_component import Component

import stores
import utils
from components import modals
from odm import odm
from stores import DatasetDict

_IGNORE_LABEL = 'Ignore'
_DUP_ERROR_PREFIX = 'Multiple sheets are mapped to table'

_versions = list(map(lambda e: e.value, odm.Version))
_version_dropdown = dcc.Dropdown(_versions, _versions[-1], clearable=False)

_filename_label = html.Span()
_mapping_table = html.Div(id='conf-dialog-mapping-table')

_ok_btn = dbc.Button('Ok')
_cancel_btn = dbc.Button('Cancel')

_duplicate_err = dbc.Alert('', color='danger', is_open=False)

_conf_dialog = modals.init_modal(
    id='conf-dialog',
    title='Configure dataset',
    body=[
        _duplicate_err,
        html.P(html.Strong(_filename_label)),
        html.Div(['ODM Version: ', _version_dropdown]),
        _mapping_table,
    ],
    buttons=[
        _ok_btn,
        _cancel_btn,
    ]
)

layout = _conf_dialog


def _find_keys(d: dict, val: str) -> List[str]:
    '''returns list of keys in dict `d` with value `val`'''
    return list(
        map(lambda pair: pair[0],
            filter(lambda pair: pair[1] == val, d.items())))


def register(app):  # type: ignore

    @app.callback(
        [
            Output(stores.conf_dialog_flag, 'data', allow_duplicate=True),
            Output(stores.datasets, 'data', allow_duplicate=True),
            Output(stores.dataset_id, 'data', allow_duplicate=True),
        ],
        Input(_cancel_btn, 'n_clicks'),
        State(stores.conf_dialog_flag, 'data'),
        State(stores.dataset_id, 'data'),
    )
    def on_cancel_btn_click(n: int, flag: bool, dataset_id: str
                            ) -> Tuple[bool, Patch, str]:
        '''close dialog. If opened from upload, then delete dataset.'''
        if flag == stores.OPEN_FROM_UPLOAD:
            p = Patch()
            del p[dataset_id]
            return False, p, ''
        return False, no_update, no_update

    @app.callback(
        [
            Output(_conf_dialog, 'is_open'),
            Output(stores.conf_dialog_init, 'data'),
        ],
        Input(stores.conf_dialog_flag, 'data'),
    )
    def on_conf_dialog_flag(flag: bool) -> Tuple[bool, bool]:
        '''open/close conf dialog'''
        return flag, (True if flag else no_update)

    @app.callback(
        [
            Output(_filename_label, 'children'),
            Output(_version_dropdown, 'value'),
            Output(_duplicate_err, 'children', allow_duplicate=True),
            Output(_duplicate_err, 'is_open', allow_duplicate=True),
        ],
        [
            Input(stores.conf_dialog_init, 'data'),
            State(stores.datasets, 'data'),
            State(stores.dataset_id, 'data'),
        ]
    )
    def on_conf_dialog_init(
        signal: bool,
        datasets: DatasetDict,
        dataset_id: str,
    ) -> Tuple[str, str, str, bool]:
        '''init conf dialog'''
        ds = datasets[dataset_id]
        version_str = ds['odm_version']
        assert version_str in _versions
        return ds['filename'], version_str, '', False

    @app.callback(
        [
            Output(_mapping_table, 'children'),
            Output(stores.dataset_conf_form, 'data', allow_duplicate=True),
        ],
        Input(_version_dropdown, 'value'),
        State(stores.datasets, 'data'),
        State(stores.dataset_id, 'data'),
    )
    def on_version_dropdown_value(
        selected_version_str: str,
        datasets: DatasetDict,
        dataset_id: str,
    ) -> Tuple[Component, dict]:
        '''initializes the mapping table with ODM table names whenever the
        selected version changes'''
        assert selected_version_str
        ds = datasets[dataset_id]
        mapping = ds['sheet_tables']
        old_version = odm.Version(ds['odm_version'])
        selected_version = odm.Version(selected_version_str)
        new_mapping = {}

        # re-infer mapping when changing version
        if selected_version != old_version:
            sheet_names = list(mapping.keys())
            mapping = odm.infer_table_mapping(sheet_names, selected_version)
            new_mapping = mapping

        odm_table_names = odm.get_table_names(selected_version)
        table_options = [_IGNORE_LABEL] + odm_table_names

        def init_dropdown(sheet: str, table: str) -> Component:
            # uses https://dash.plotly.com/pattern-matching-callbacks to
            # enable callbacks with dynamically generated components
            values = table_options
            current = table if table else _IGNORE_LABEL
            id = {
                'type': 'sheet-table-dropdown',
                'index': sheet,
            }
            return dcc.Dropdown(values, current, id=id, clearable=False)

        sheet_dropdowns = {
            sheet: init_dropdown(sheet, table)
            for sheet, table in mapping.items()
        }

        html_table = html.Table([
            html.Thead(html.Tr([html.Th('Sheet'), html.Th('ODM Table')])),
            html.Tbody([
                html.Tr([html.Td(sheet), html.Td(dropdown)])
                for sheet, dropdown in sheet_dropdowns.items()
            ])
        ])

        return html_table, new_mapping

    @app.callback(
        Output(stores.dataset_conf_form, 'data'),
        Input({'type': 'sheet-table-dropdown', 'index': ALL}, 'value'),
        State({'type': 'sheet-table-dropdown', 'index': ALL}, 'id'),
        State(stores.datasets, 'data'),
        State(stores.dataset_id, 'data'),
    )
    def on_sheet_table_dropdown_value(
        dropdown_values: List[str],
        dropdown_ids: List[str],
        datasets: DatasetDict,
        dataset_id: str,
    ) -> Patch:
        '''Update the sheet-table mapping, when a table is selected. Any
        previous mappings to the same table will be set to ignored.

        :param dropdown_values: table names, including the 'ignore' item.
        '''
        dropdown_id = callback_context.triggered_id
        sheet = dropdown_id['index']
        table_ix = dropdown_ids.index(dropdown_id)
        table = dropdown_values[table_ix]
        assert table, 'table should not be None or an empty string'
        patch = Patch()
        patch[sheet] = table if table != _IGNORE_LABEL else ''
        return patch

    @app.callback(
        [
            Output(_duplicate_err, 'is_open', allow_duplicate=True),
            Output(_duplicate_err, 'children', allow_duplicate=True),
            Output(stores.conf_dialog_flag, 'data', allow_duplicate=True),
            Output(stores.datasets, 'data', allow_duplicate=True),
            Output('url', 'pathname'),
        ],
        [
            Input(_ok_btn, 'n_clicks'),
            State(_version_dropdown, 'value'),
            State(stores.dataset_conf_form, 'data'),
            State(stores.datasets, 'data'),
            State(stores.dataset_id, 'data'),
        ],
    )
    def on_ok_btn_click(
        n: int,
        version_str: str,
        new_mapping: dict,
        datasets: DatasetDict,
        dataset_id: str,
    ) -> Tuple[bool, str, bool, Patch, str]:
        '''update dataset config with table mapping, and close conf dialog'''
        ds = datasets[dataset_id]
        ds['odm_version'] = version_str
        filename = ds['filename']
        mapping = ds['sheet_tables']
        for sheet, table in new_mapping.items():
            mapping[sheet] = table

        # check for duplicates
        selected_tables = list(filter(bool, mapping.values()))
        dup_tables = utils.duplicates(selected_tables)
        if len(dup_tables) > 0:
            entries: List[str] = []
            for table in dup_tables:
                keys = _find_keys(mapping, table)
                entries.append(html.Span([
                    f'{_DUP_ERROR_PREFIX} "{table}": ',
                    utils.gen_html_list(keys),
                ]))
            error_list = utils.gen_html_list(entries)
            return (True, error_list) + (no_update,)*3

        patch = Patch()
        patch[filename] = ds
        return (
            False,  # error flag
            '',     # error msg
            False,  # conf dialog
            patch,  # datasets
            utils.get_dataset_path(filename),  # url
        )
