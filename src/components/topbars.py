import dash_bootstrap_components as dbc
from dash import (
    Input,
    Output,
)

import stores
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

topbar = dbc.NavbarSimple(
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
)


def register(app):

    @app.callback(
        Output(stores.upload_dialog_flag, 'data', allow_duplicate=True),
        Input(menu_upload_btn, 'n_clicks'),
    )
    def on_upload_btn(n):
        """Set upload dialog flag"""
        return bool(n)

    @app.callback(
        Output(menu_dataset_dropdown, 'children'),
        Input(stores.datasets, 'data'),
        prevent_initial_call=False,
    )
    def on_datasets(datasets):
        """Update dataset dropdown"""
        # This shouldn't equire any extra network traffic since it's triggering
        # on already uploaded datasets.
        if not datasets:
            return [dbc.DropdownMenuItem('No datasets uploaded')]
        else:
            return list(map(lambda name: dbc.DropdownMenuItem(name), datasets))
