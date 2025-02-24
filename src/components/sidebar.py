from operator import itemgetter
from itertools import groupby

import dash_bootstrap_components as dbc
from dash import (
    Input,
    Output,
    State,
    dcc,
    html,
    no_update,
)
from dash.development.base_component import Component

import stores
import utils

conf_btn = dbc.NavLink('Configure')
share_btn = dbc.NavLink('Share')
validate_btn = dbc.NavLink('Validate')
validation_list = html.Div()

layout = html.Div(
    [
        html.Strong("Dataset Actions"),
        dbc.Nav(
            [
                conf_btn,
                validate_btn,
                share_btn,
            ],
            vertical="md",
        ),
        html.Br(),
        html.Strong('Validations'),
        validation_list,
    ],
    id='sidebar',
)


def register(app):  # type: ignore

    def open_dialog(n: int) -> bool:
        return True if n else no_update

    @app.callback(
        Output(stores.conf_dialog_flag, 'data'),
        Input(conf_btn, 'n_clicks'),
    )
    def on_conf_btn_click(n: int) -> bool:
        '''open conf dialog'''
        return open_dialog(n)

    @app.callback(
        Output(stores.validation_dialog_flag, 'data', allow_duplicate=True),
        Input(validate_btn, 'n_clicks'),
    )
    def on_validation_btn(n: int) -> bool:
        '''open new-validation dialog'''
        return open_dialog(n)

    @app.callback(
        Output(validation_list, 'children', allow_duplicate=True),
        Input(stores.validations, 'data'),
        State('url', 'pathname'),
        prevent_initial_call=False,
    )
    def on_validations(validations: dict, pathname: str) -> Component:
        # get dataset id from dataset or validation url
        dataset_id = utils.get_dataset_id(pathname)
        if not dataset_id:
            (dataset_id, _) = utils.get_validation_id(pathname)
        assert dataset_id

        def get_nameurl(validation_name: str) -> tuple[str, str]:
            name = validation_name
            url = utils.get_validation_path(dataset_id, name)
            return (name, url)

        def get_link(nameurl: tuple[str, str]) -> Component:
            name, url = nameurl
            return dcc.Link(name, href=url)

        # gen validation links from dataset id and validation names
        ds_validations = validations.get(dataset_id, {})
        if len(ds_validations) == 0:
            return 'None'

        named_revisions = list(map(lambda x: (x[0], x[1]['ds_revision']),
                                   ds_validations.items()))
        named_revisions.sort(key=itemgetter(1))
        group_iter = groupby(named_revisions, key=itemgetter(1))
        rev_names = {
            rev: list(map(itemgetter(0), names)) for (rev, names) in group_iter
        }

        rev_links = {}
        for rev, names in reversed(rev_names.items()):
            rev_text = f'rev. {rev}'
            links = list(map(get_link, map(get_nameurl, reversed(names))))
            rev_links[rev_text] = links

        return utils.gen_html_list(rev_links)

    @app.callback(
        Output(stores.share_dialog_flag, 'data', allow_duplicate=True),
        Input(share_btn, 'n_clicks'),
    )
    def on_share_btn(n: int) -> bool:
        '''open share dialog'''
        return open_dialog(n)
