import json
from pprint import pformat
from typing import (
    Optional,
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
)
from dash.development.base_component import Component
import dash_bootstrap_components as dbc

import stores
import utils
from components import sidebar

# XXX: validation_name is called name and not id because the name doesn't
# identify the validation by itself, since it depends on dataset_id, so the
# actual "validation id" would be dataset_id + validation_name

# XXX: dash doesn't support sub-pages, so validations has to be it's own page
# even tho it's "under" datasets.
PAGE_URL = '/validations/<dataset_id>/<validation_name>'

dash.register_page(__name__, path_template=PAGE_URL)

_page_content = html.Div()


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
        _page_content,
    ])


@callback(
    [
        Output(_page_content, 'children'),
        Output(stores.dataset_id, 'data', allow_duplicate=True),
    ],
    Input(_page_content, 'children'),
    State('url', 'pathname'),
    State(stores.validations, 'data'),
    prevent_initial_call='initial_duplicate',
)
def on_page_load(dummy: Component, pathname: str, validations: dict
                 ) -> Tuple[Component, str]:
    # XXX: uses an iframe as a hack to preserve formatting
    (dataset_id, validation_name) = utils.get_validation_id(pathname)
    v = validations[dataset_id][validation_name]
    report = json.loads(v['report'])

    # XXX: tmp fix to reduce browser lag/crash due to extreme amount of
    # text from big datasets
    def remove_excess(es: list) -> None:
        del es[100:]
        for e in es:
            e.pop('row', None)
            e.pop('rows', None)
            e.pop('validationRuleFields', None)
            e.pop('message', None)
    remove_excess(report.get('errors', []))
    remove_excess(report.get('warnings', []))

    report_text = pformat(report)
    content = [
        html.P('placeholder validation summary, first 100 only:'),
        html.Iframe(srcDoc=f'<pre><code>{report_text}</code></pre>'),
        dbc.Button('View validation report'),
    ]
    return content, dataset_id
