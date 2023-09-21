import dash_bootstrap_components as dbc
from dash import (
    html,
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
