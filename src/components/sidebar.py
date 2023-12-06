from typing import Tuple

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

conf_btn = dbc.Button('Configure Dataset')
validate_btn = dbc.Button('Validate Dataset')
validation_list = html.Div('None')

layout = html.Div(
    [
        html.Div([
            conf_btn,
            validate_btn,
        ]),
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

        def get_nameurl(validation_name: str) -> Tuple[str, str]:
            name = validation_name
            url = utils.get_validation_path(dataset_id, name)
            return (name, url)

        def get_link(nameurl: Tuple[str, str]) -> Component:
            name, url = nameurl
            return dcc.Link(name, href=url)

        # gen validation links from dataset id and validation names
        names = validations.get(dataset_id, {}).keys()
        name_urls = map(get_nameurl, names)
        links = map(get_link, name_urls)
        return utils.gen_html_list(list(links))
