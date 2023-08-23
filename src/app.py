import dash
import dash_bootstrap_components as dbc
from dash import (
    Dash,
    html,
)

stylesheets = [
    dbc.themes.BOOTSTRAP,
    'https://codepen.io/chriddyp/pen/bWLwgP.css'
]

app = Dash(__name__, use_pages=True, external_stylesheets=stylesheets,
           prevent_initial_callbacks=True)

main_menu = [
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
    children=main_menu,
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
    style={
        'position': 'fixed',
        'top': 44,
        'left': 0,
        'bottom': 0,
        'width': '16rem',
        'padding': '2rem 1rem',
        'background-color': '#f8f9fa',
    },
)

app.layout = html.Div([
    topbar,
    sidebar,
    html.Div(
        dash.page_container,
        id="page-content",
        style={
            'margin-left': '18rem',
            'margin-right': '2rem',
            'padding': '2rem 1rem',
        },
    ),
])


if __name__ == '__main__':
    app.run_server(debug=True)
