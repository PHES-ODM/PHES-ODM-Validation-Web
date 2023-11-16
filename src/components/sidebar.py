import dash_bootstrap_components as dbc
from dash import (
    Input,
    Output,
    html,
    no_update,
)

import stores

conf_btn = dbc.Button('Configure Dataset')

layout = html.Div(
    [
       conf_btn,
       dbc.Button('Validate Dataset', disabled=True),
    ],
    id='sidebar',
)


def register(app):

    @app.callback(
        Output(stores.conf_dialog_flag, 'data'),
        Input(conf_btn, 'n_clicks'),
    )
    def on_conf_btn_click(n):
        '''open conf dialog'''
        return True if n else no_update
