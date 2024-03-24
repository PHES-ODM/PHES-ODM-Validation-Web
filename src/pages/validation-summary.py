from itertools import groupby
# from pprint import pformat, pprint
from typing import (
    List,
    Optional,
    Set,
    Tuple,
)
from urllib.parse import unquote

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
import dash_bootstrap_components as dbc

from odm_validation.rules import RuleId
from odm_validation.reports import ErrorKind
from odm_validation.summarization import ErrorSummary, SummaryEntry, SummaryKey

import stores
import utils
from components import sidebar

# XXX: validation_name is called name and not id because the name doesn't
# identify the validation by itself, since it depends on dataset_id, so the
# actual "validation id" would be dataset_id + validation_name

# XXX: dash doesn't support sub-pages, so validations has to be it's own page
# even tho it's "under" datasets.
PAGE_URL_PREFIX = 'validations'
PAGE_URL = f'/{PAGE_URL_PREFIX}/<dataset_id>/<validation_name>'

dash.register_page(__name__, path_template=PAGE_URL)

_view_report_btn = dbc.Button('View validation report')
_page_content = html.Div()
_trigger = html.Div(id='trigger')


def layout(
    dataset_id: Optional[str] = None,
    validation_name: Optional[str] = None
) -> Component:
    dataset_id = unquote(dataset_id or '')
    validation_name = unquote(validation_name or '')
    return html.Div([
        sidebar.layout,
        html.H1('Dataset Validation Summary'),
        html.H2(dataset_id),
        html.H3(validation_name),
        _trigger,
        _page_content,
        html.Br(),
        _view_report_btn,
    ])


# TODO: optimize using clientside callback to avoid big data transfer
@callback(
    [
        Output(_page_content, 'children'),
        Output(stores.dataset_id, 'data', allow_duplicate=True),
    ],
    Input(_trigger, 'id'),
    State('url', 'pathname'),
    State(stores.datasets, 'data'),
    State(stores.validation_summaries, 'data'),
    prevent_initial_call='initial_duplicate',
)
def on_page_load(dummy: Component, pathname: str,
                 datasets: dict, summaries: dict
                 ) -> Tuple[Component, str]:
    # - number of invalid tables (excel)
    # - for each table:
    #   - number of errors
    #   - number of warnings
    #   - number of invalid columns
    #   - number of invalid rows

    def get_value_set(es: ErrorSummary) -> Set[str]:
        return set(map(lambda e: e['value'], es))

    def get_entries(
        summary: dict,
        kind: ErrorKind,
        table: str,
        key: SummaryKey
    ) -> List[SummaryEntry]:
        es = summary[kind.value + 's'].get(table, [])
        return list(filter(lambda e: e['key'] == key, es))

    def get_count(es: List[dict], rule_id: RuleId) -> int:
        e: dict = next(filter(lambda e: e['rule_id'] == rule_id.value, es), {})
        return e.get('count', 0)

    (dataset_id, validation_name) = utils.get_validation_id(pathname)

    ds = datasets[dataset_id]
    sheet_tables = ds['sheet_tables']

    report_summary = summaries[dataset_id][validation_name]

    # tables
    # XXX: validations can't be read with an updated version of the app, if
    # RuleId value changes in the next version
    rs = report_summary
    table_errors = []
    for sheet, table in sheet_tables.items():
        if not table:
            continue
        es = get_entries(rs, ErrorKind.ERROR, table, SummaryKey.TABLE)
        ws = get_entries(rs, ErrorKind.WARNING, table, SummaryKey.TABLE)
        num_errors = get_count(es, RuleId._all)
        num_warnings = get_count(ws, RuleId._all)

        es = get_entries(rs, ErrorKind.ERROR, table, SummaryKey.ROW)
        invalid_rows = list(get_value_set(es))
        total_rows = ds['table_sizes'][table]

        table_errors.append({
            'Table': table,
            'Warnings': num_warnings,
            'Errors': num_errors,
            'Erroneous Rows': len(invalid_rows),
            'Total Rows': total_rows,
        })

    def getrows(table: str, es: List[SummaryEntry]) -> List[dict]:
        def getkey(e: SummaryEntry) -> str:
            return e['value']
        result = []
        es = sorted(es, key=getkey)
        for key, group in groupby(es, getkey):
            count = sum(map(lambda e: e['count'], group))
            result.append({
                'Table': table,
                'Column': key,
                'Errors': count,
            })
        return result

    col_errors = []
    for table in sheet_tables.values():
        if not table:
            continue
        es = get_entries(rs, ErrorKind.ERROR, table, SummaryKey.COLUMN)
        col_errors += getrows(table, es)

    col_section = [
        utils.gen_html_table(col_errors)
    ]

    content = [
        html.H4('Tables'),
        utils.gen_html_table(table_errors),
        html.H4('Columns'),
        # utils.gen_html_table(col_errors),
    ] + col_section
    return content, dataset_id


@callback(
    Output(stores.report_dialog_flag, 'data'),
    Input(_view_report_btn, 'n_clicks'),
    prevent_initial_call=True,
)
def on_view_report_btn_click(n: int) -> bool:
    if not n:
        return no_update
    return True
