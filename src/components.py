import dash_bootstrap_components as dbc
from dash import (
    html,
)

_main_menu = [
    dbc.NavItem(dbc.NavLink('Upload dataset')),
    dbc.DropdownMenu(
        label='Datasets',
        children=[
            dbc.DropdownMenuItem('No datasets uploaded'),
        ],
        nav=True,
        in_navbar=True,
    ),
    dbc.NavItem(dbc.NavLink('Validation profiles')),
    dbc.NavItem(dbc.NavLink('Tutorial')),
]

topbar = dbc.NavbarSimple(
    children=_main_menu,
    brand="ODM Validation",
    brand_href="/",
    color="primary",
    dark=True,
)

sidebar = html.Div(
    [
        dbc.Nav(
            [
                dbc.NavLink('sidebar 1', href='#'),
                dbc.NavLink('sidebar 2', href='#'),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    id='sidebar',
)
