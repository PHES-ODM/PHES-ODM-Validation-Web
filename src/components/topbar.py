from typing import List

import dash_bootstrap_components as dbc
from dash import (
    Input,
    Output,
)
from dash.development.base_component import Component

import stores
import utils
from stores import DatasetDict
# from utils import echo

menu_upload_btn = dbc.NavLink('Upload dataset', id='menu-upload-btn')

# The children for the dropdown are initializes in the on_datasets callback
# below. This way every time the user modified the Datasets store, the dropdown
# items are kept synchronized.
menu_dataset_dropdown = dbc.DropdownMenu(
    label='Datasets',
    nav=True,
    in_navbar=True,
)

_topbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(menu_upload_btn),
        menu_dataset_dropdown,
        dbc.NavItem(dbc.NavLink('Validation profiles')),
        dbc.NavItem(dbc.NavLink('Tutorial')),
    ],
    brand="ODM Validation",
    brand_href="/",
    color="primary",
    dark=True,
    fixed="top"
)

layout = _topbar


def register(app):  # type: ignore

    @app.callback(
        Output(stores.upload_dialog_flag, 'data', allow_duplicate=True),
        Input(menu_upload_btn, 'n_clicks'),
    )
    def on_upload_btn_click(n: int) -> bool:
        """Set upload dialog flag"""
        return bool(n)

    @app.callback(
        Output(menu_dataset_dropdown, 'children'),
        Input(stores.datasets, 'data'),
        prevent_initial_call=False,
    )
    def on_datasets(datasets: DatasetDict) -> List[Component]:
        """Update dataset dropdown"""
        # This shouldn't equire any extra network traffic since it's triggering
        # on already uploaded datasets.
        if not datasets:
            return [dbc.DropdownMenuItem('No datasets uploaded')]
        result = []
        for name in datasets:
            url = utils.get_dataset_path(name)
            item = dbc.DropdownMenuItem(name, href=url)
            result.append(item)
        return result
