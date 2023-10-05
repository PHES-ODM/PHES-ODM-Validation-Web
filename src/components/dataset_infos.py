import logging
from urllib.parse import parse_qs

from dash import (
    Input,
    Output,
    State,
    html,
)
from dash.dash import no_update

import stores

dataset_info = html.Div(id='dataset-info')


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


def register(app):
    @app.callback(
        Output(dataset_info, 'children'),
        Input('url', 'pathname'),
        State('url', 'search'),
        State(stores.datasets, 'data'),
        prevent_initial_call=False,
    )
    def on_datasets_page(pathname, query, datasets):
        if pathname != '/datasets' or not datasets:
            return no_update
        params = parse_qs(query[1:])
        logging.info(params)
        names = params.get('dataset-id')
        if not names:
            logging.error('missing dataset id param')
            return no_update
        name = names[0]
        ds = datasets.get(name)
        if not ds:
            logging.error(f'invalid dataset id "{name}"')
            return no_update
        return [
            html.H2(name),
            html.P([html.Strong('ODM version: '), ds['odm_version']]),
            html.P(html.Strong('ODM tables')),
            _gen_odm_table_list(ds['table_names']),
            html.P(html.Strong('Unknown tables')),
            _gen_unknown_table_list(ds['table_names']),
        ]
