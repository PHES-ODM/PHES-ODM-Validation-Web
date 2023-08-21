import base64
import datetime
import io
import os
import sys
from os.path import join

import dash
from dash import (
    dcc,
    html,
)

src_dir = join(os.path.dirname(os.path.realpath(__file__)), '..')
sys.path.append(src_dir)

dash.register_page(__name__, path='/datasets')

upload_dialog = html.Div([
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files'),
        ]),
        multiple=False,
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        }
    ),
    html.Div(id='upload-status'),
])

conf_table = html.Div([
    html.Div(id='conf-table'),
])

layout = html.Div([
    html.H2('Datasets'),
])
