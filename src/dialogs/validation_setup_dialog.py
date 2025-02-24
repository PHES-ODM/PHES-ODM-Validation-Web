import dash_bootstrap_components as dbc
from dash import (
    Input,
    Output,
    State,
    dcc,
    html,
    no_update,
)
from dash.development.base_component import Component

from odm_validation.rules import RuleId

import stores
import utils
from components import modals
from stores import ValidationSetup

from dialogs.common import register_dialog_flag_callback

DUP_ERR_MSG = 'Validation name already exists'
ODM_PROFILE = 'ODM profile'
VALIDATION_NAME_FMT = 'Validation {n}'

RULE_NAMES = list(
    filter(lambda x: not x.startswith('_'),
           map(lambda x: x.name, RuleId)))

cancel_btn = dbc.Button('Cancel')
customize_btn = dbc.Button('Customize')
duplicate_err = dbc.Alert(DUP_ERR_MSG, color='danger', is_open=False)
profile_dropdown = dcc.Dropdown([ODM_PROFILE], ODM_PROFILE, clearable=False)
start_btn = dbc.Button('Start')
validation_name_text = dcc.Input(type='text')
validation_rules = html.Div()

_validation_dialog = modals.init_modal(
    id='validation-dialog',
    title='New validation',
    body=[
        duplicate_err,
        html.Strong('Name'),
        html.Div([
            html.Div(validation_name_text),
        ]),
        html.Strong('Profile'),
        html.Div(profile_dropdown),
        html.Strong('Profile rules'),
        validation_rules,
    ],
    buttons=[
        customize_btn,
        start_btn,
        cancel_btn,
    ]
)

layout = _validation_dialog


def toLower(s: str) -> str:
    return s.lower()


def get_next_name(cased_names: list) -> str:
    names = set(map(toLower, cased_names))
    n = len(names) + 1
    while True:
        name = VALIDATION_NAME_FMT.format(n=n)
        if name.lower() not in names:
            return name
        n += 1


def register(app):  # type:ignore
    register_dialog_flag_callback(app, _validation_dialog,
                                  stores.validation_dialog_flag,
                                  stores.validation_dialog_init)

    @app.callback(
        Output(stores.validation_dialog_flag, 'data', allow_duplicate=True),
        Input(cancel_btn, 'n_clicks'),
    )
    def on_cancel_btn(n: int) -> bool:
        '''close dialog'''
        return False

    @app.callback(
        [
            Output(validation_name_text, 'value'),
            Output(validation_rules, 'children'),
        ],
        Input(stores.validation_dialog_init, 'data'),
        State(stores.dataset_id, 'data'),
        State(stores.validations, 'data'),
    )
    def on_dialog_init(signal: bool, dataset_id: str, validations: dict
                       ) -> tuple[str, Component]:
        '''init dialog'''
        names = validations.get(dataset_id, [])
        name = get_next_name(names)
        rules = utils.gen_html_list(RULE_NAMES)
        return name, rules

    @app.callback(
        [
            Output(duplicate_err, 'is_open'),
            Output(stores.validation_dialog_flag, 'data',
                   allow_duplicate=True),
            Output(stores.progress_dialog_flag, 'data', allow_duplicate=True),
            Output(stores.validation_setup, 'data', allow_duplicate=True),
        ],
        Input(start_btn, 'n_clicks'),
        State(validation_name_text, 'value'),
        State(profile_dropdown, 'value'),
        State(stores.dataset_id, 'data'),
        State(stores.validations, 'data'),
    )
    def on_start_btn(
        n: int,
        validation_name: str,
        profile_id: str,
        dataset_id: str,
        validations: dict,
    ) -> tuple[bool, bool, bool, ValidationSetup]:
        '''validate validation name, close dialog, open validation-progress
        dialog'''
        if validation_name in validations.get(dataset_id, {}):
            return (True,) + (no_update,)*3
        setup = ValidationSetup(
            dataset_id=dataset_id,
            validation_name=validation_name,
            profile_id=profile_id,
        )
        return (
            False,  # error
            False,  # dialog flag
            True,   # dialog flag
            setup,  # validation setup
        )
