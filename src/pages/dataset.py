import logging
from typing import (
    Dict,
    List,
    Optional,
)

import dash
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
from odm import odm
from stores import Dataset

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
    table_headers: Dict[odm.TableName, List[str]],
    table_sizes: Dict[odm.TableName, int],
) -> Component:
    entries: List[Component] = []
    for sheet, table, in sheet_tables.items():
        if not table:
            continue
        num_rows = table_sizes[table]
        cols = set(table_headers[table])
        num_cols = len(cols)
        all_odm_cols = set(odm.get_column_names(version, table))
        odm_cols = all_odm_cols.intersection(cols)
        ignored_cols = cols - odm_cols

        entry = html.Li([
            html.Strong(table),
            f' ⟵ "{sheet}":',
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
    sheet_tables: Dict[str, str]
) -> Component:
    entries: List[html.Li] = []
    for a, b, in sheet_tables.items():
        if not b:
            entries.append(html.Li(f'"{a}"'))
    return html.Ul(entries)


def _init_upload_report(ds: Dataset) -> List[Component]:
    def entry(key: str, val: Component = '') -> Component:
        return html.P([html.Strong(key + ': '), val])

    timestr = ds['upload_time']
    sheet_tables = ds['sheet_tables']
    num_sheets = len(sheet_tables)
    num_odm_tables = len(list(filter(bool, sheet_tables.values())))
    ver_str = ds['odm_version']
    ver = odm.Version(ver_str)
    num_ignored_tables = num_sheets - num_odm_tables

    return [
        entry('Revision', ds['revision']),
        entry('Upload time', timestr),
        entry('ODM version', ver_str),
        entry(f'ODM tables ({num_odm_tables})'),
        _gen_odm_table_list(ver, sheet_tables, ds['table_headers'],
                            ds['table_sizes']),
        entry(f'Ignored sheets ({num_ignored_tables})'),
        _gen_unknown_table_list(sheet_tables),
    ]


# TODO: optimize sheet load with client callback
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


@callback(
    Output(stores.dataset_id, 'data', allow_duplicate=True),
    Input('url', 'pathname'),
    prevent_initial_call='initial_duplicate',
)
def on_url_pathname(pathname: str) -> str:
    '''sets dataset_id from pathname on page load'''
    # XXX: This can't be combined with on_dataset_page because:
    # - dataset_id output requires allow_duplicate
    # - allow_duplicate requires prevent_initial_call='initial_duplicate'
    # - prevent_initial_call not being False causes dash to complain about the
    #   on_dataset_page output (_page_content) component not existing yet
    ds_id = utils.get_dataset_id(pathname)
    return ds_id if ds_id else no_update
