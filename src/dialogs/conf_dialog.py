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

IGNORE_LABEL = 'Ignore'

_versions = list(map(lambda e: e.value, odm.Version))
version_dropdown = dcc.Dropdown(_versions, _versions[-1], clearable=False)

filename_label = html.Span()
mapping_table = html.Div(id='conf-dialog-mapping-table')

ok_btn = dbc.Button('Ok')
cancel_btn = dbc.Button('Cancel')

duplicate_err = dbc.Alert('', color='danger', is_open=False)
_duplicate_err_msg = 'multiple sheets are mapped to the same table: '

# this store is only used by this module
'''type: list of dropdown ids'''

_conf_dialog = modals.init_modal(
    id='conf-dialog',
    title='Configure dataset',
    body=[
        duplicate_err,
        html.P(html.Strong(filename_label)),
        html.Div(['ODM Version: ', version_dropdown]),
        mapping_table,
    ],
    buttons=[
        ok_btn,
        cancel_btn,
    ]
)

layout = _conf_dialog


def register(app):  # type: ignore

    @app.callback(
        [
            Output(stores.conf_dialog_flag, 'data', allow_duplicate=True),
            Output(stores.datasets, 'data', allow_duplicate=True),
            Output(stores.dataset_id, 'data', allow_duplicate=True),
        ],
        Input(cancel_btn, 'n_clicks'),
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
            Output(filename_label, 'children'),
            Output(version_dropdown, 'value'),
        ],
        [
            Input(stores.conf_dialog_flag, 'data'),
            State(stores.datasets, 'data'),
            State(stores.dataset_id, 'data'),
        ]
    )
    def on_conf_dialog_flag(
        flag: bool,
        datasets: DatasetDict,
        dataset_id: str,
    ) -> Tuple[bool, str, str]:
        '''open/close conf dialog when flag changes'''
        if not flag:
            return flag, no_update, no_update
        ds = datasets[dataset_id]
        version_str = ds['odm_version']
        assert version_str in _versions
        return flag, ds['filename'], version_str

    @app.callback(
        [
            Output(mapping_table, 'children'),
            Output(stores.dataset_conf_form, 'data', allow_duplicate=True),
        ],
        Input(version_dropdown, 'value'),
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
        mapping = ds['table_mapping']
        old_version = odm.Version(ds['odm_version'])
        selected_version = odm.Version(selected_version_str)
        new_mapping = {}

        # re-infer mapping when changing version
        if selected_version != old_version:
            sheet_names = list(mapping.keys())
            mapping = odm.infer_table_mapping(sheet_names, selected_version)
            new_mapping = mapping

        odm_table_names = odm.get_table_names(selected_version)
        table_options = [IGNORE_LABEL] + odm_table_names

        def init_dropdown(sheet: str, table: str) -> Component:
            # uses https://dash.plotly.com/pattern-matching-callbacks to
            # enable callbacks with dynamically generated components
            values = table_options
            current = table if table else IGNORE_LABEL
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
        patch[sheet] = table if table != IGNORE_LABEL else ''
        return patch

    @app.callback(
        [
            Output(duplicate_err, 'is_open'),
            Output(duplicate_err, 'children'),
            Output(stores.conf_dialog_flag, 'data', allow_duplicate=True),
            Output(stores.datasets, 'data', allow_duplicate=True),
            Output('url', 'pathname'),
        ],
        [
            Input(ok_btn, 'n_clicks'),
            State(version_dropdown, 'value'),
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
        mapping = ds['table_mapping']
        for sheet, table in new_mapping.items():
            mapping[sheet] = table

        # check for duplicates
        selected_tables = list(filter(bool, mapping.values()))
        dup_tables = utils.duplicates(selected_tables)
        if len(dup_tables) > 0:
            msg = _duplicate_err_msg + ', '.join(dup_tables)
            return (True, msg) + (no_update)*3

        patch = Patch()
        patch[filename] = ds
        return (
            False,  # duplicate_err
            '',     # duplicate_err msg
            False,  # conf dialog
            patch,  # datasets
            utils.get_dataset_path(filename),  # url
        )
