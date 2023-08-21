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


def gen_menu_link(page):
    name = page['name']
    path = page['relative_path']
    if name == 'Datasets':
        return dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem('a', href='/datasets'),
                dbc.DropdownMenuItem('b', href='/datasets'),
            ],
            nav=True,
            in_navbar=True,
            label=name,
        )
    else:
        return dbc.NavItem(dbc.NavLink(name, href=path))


topbar = dbc.NavbarSimple(
    children=list(map(gen_menu_link, dash.page_registry.values())),
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
