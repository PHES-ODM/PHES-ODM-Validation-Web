import dash
from dash import (
    html,
)

import components.dataset_infos as di

dash.register_page(__name__, path='/datasets')

layout = html.Div([
    html.H1('Dataset Info'),
    di.dataset_info,
])
