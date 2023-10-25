import logging

import dash
from dash import (
    Input,
    Output,
    State,
    callback,
    html,
    no_update,
)

import stores

dash.register_page(__name__, path_template='/datasets/<dataset_id>')

layout = html.Div()


def _gen_odm_table_list(table_names):
    entries = []
    for a, b, in table_names.items():
        if b:
            entries.append(html.Li(f'"{a}" ({b})'))
    return html.Ul(entries)


def _gen_unknown_table_list(table_names):
    entries = []
    for a, b, in table_names.items():
        if not b:
            entries.append(html.Li(f'"{a}"'))
    return html.Ul(entries)


@callback(
    Output(layout, 'children'),
    Input('url', 'pathname'),
    State(stores.datasets, 'data'),
)
def init_dataset_page(pathname, datasets):
    if not (pathname.startswith('/datasets') and datasets):
        return no_update
    dataset_id = pathname[(pathname.rfind('/')+1):]
    logging.error('init_dataset_page ' + dataset_id)
    ds = datasets.get(dataset_id)
    if not ds:
        logging.error(f'invalid dataset "{dataset_id}"')
        return no_update
    return html.Div([
        html.H1('Dataset Info'),
        html.H2(dataset_id),
        html.P([html.Strong('ODM version: '), ds['odm_version']]),
        html.P(html.Strong('ODM tables')),
        _gen_odm_table_list(ds['table_names']),
        html.P(html.Strong('Unknown tables')),
        _gen_unknown_table_list(ds['table_names']),
    ])
