import dash
from dash import (
    html,
)

dash.register_page(__name__, path='/')

layout = html.Div([
    html.H1('Welcome'),
    html.H2('to the ODM Validation web tool!'),
    html.P('Here you can upload and validate your ODM compliant datasets.'),
    html.P('See tutorials for more info.'),
])
