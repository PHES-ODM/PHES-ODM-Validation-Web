"""This sample shows that the memory store persists across pages"""

import datetime

import dash
from dash import (
    Dash,
    Input,
    Output,
    callback,
    dcc,
    html,
)

app = Dash(__name__, use_pages=True, pages_folder="")

dash.register_page("home",  path='/', layout=html.Div('Home Page'))
dash.register_page("analytics", layout=html.Div('Analytics'))

store = dcc.Store(id='store', data=datetime.datetime.now())
trigger = html.Div(id='trigger')
timestamp = html.Div(id='timestamp')

app.layout = html.Div([
    store,
    trigger,
    timestamp,
    html.Div(
        [
            html.Div(
                dcc.Link(
                    f"{page['name']} - {page['path']}",
                    href=page["relative_path"]
                )
            )
            for page in dash.page_registry.values()
        ]
    ),
    dash.page_container,
])


@callback(
    Output(timestamp, 'children'),
    Input(store, 'data'),
)
def on_data(x):
    return x


if __name__ == '__main__':
    app.run(debug=True)
