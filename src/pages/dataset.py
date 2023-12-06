import logging
from typing import (
    Dict,
    List,
    Optional,
)

import dash
import dash.dcc as dcc
from dash import (
    Input,
    Output,
    State,
    callback,
    html,
    no_update,
)
from dash.development.base_component import Component

import stores
import utils
from components import sidebar
from dataset_import import Dataset, TableData
from odm import odm

PAGE_URL = '/datasets/<dataset_id>'

dash.register_page(__name__, path_template=PAGE_URL)

_page_content = html.Div(id='dataset-page-content')


def layout(dataset_id: Optional[str] = None) -> Component:
    return html.Div([
        sidebar.layout,
        html.H1('Dataset'),
        html.H2(dataset_id),
        _page_content,
    ])


def _fmt_list(values: List[str]) -> str:
    return ', '.join(values)


def _gen_odm_table_list(
    version: odm.Version,
    sheet_tables: Dict[str, str],
    table_data: Dict[odm.TableName, TableData],
) -> Component:
    entries: List[Component] = []
    for sheet, table, in sheet_tables.items():
        if not table:
            continue
        data = table_data[sheet]

        num_rows = len(data)
        num_cols = len(data[0]) if num_rows > 0 else 0
        cols = set(data[0].keys())
        all_odm_cols = set(odm.get_column_names(version, table))
        odm_cols = all_odm_cols.intersection(cols)
        ignored_cols = cols - odm_cols

        entry = html.Li([
            f'"{sheet}" ⇒ {table}:',
            html.Ul(
                [
                    html.Li(f'{num_cols} columns, {num_rows} rows'),
                    html.Li(f'{len(odm_cols)} ODM columns: ' +
                            f'{_fmt_list(list(odm_cols))}'),
                    html.Li(f'{len(ignored_cols)} Ignored columns: ' +
                            f'{_fmt_list(list(ignored_cols))}'),
                ],
                className='compact-list'
            ),
        ])

        entries.append(entry)
    return html.Ul(entries)


def _gen_unknown_table_list(
    table_mapping: Dict[str, str]
) -> Component:
    entries: List[html.Li] = []
    for a, b, in table_mapping.items():
        if not b:
            entries.append(html.Li(f'"{a}"'))
    return html.Ul(entries)


def _init_upload_report(ds: Dataset) -> List[Component]:
    def entry(key: str, val: Component = '') -> Component:
        return html.P([html.Strong(key + ': '), val])

    timestr = ds['upload_time']
    table_mapping = ds['table_mapping']
    num_sheets = len(table_mapping)
    num_odm_tables = len(list(filter(bool, table_mapping.values())))
    ver_str = ds['odm_version']
    ver = odm.Version(ver_str)
    num_ignored_tables = num_sheets - num_odm_tables

    return [
        entry('Upload time', timestr),
        entry('ODM version', ver_str),
        entry(f'ODM tables ({num_odm_tables})'),
        _gen_odm_table_list(ver, table_mapping, ds['tables']),
        entry(f'Ignored tables ({num_ignored_tables})'),
        _gen_unknown_table_list(table_mapping),
    ]


@callback(
    Output(_page_content, 'children'),
    Input(stores.datasets, 'data'),
    State('url', 'pathname'),
)
def on_dataset_page(
    datasets: Dict[str, Dataset],
    pathname: str,
) -> Component:
    '''(re)initializes the dataset page on load and when changed'''
    dataset_id = utils.get_dataset_id(pathname)
    logging.info(f'dataset id: {dataset_id}')
    ds = datasets.get(dataset_id)
    if not ds:
        return no_update
    return _init_upload_report(ds)
