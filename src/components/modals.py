import dash_bootstrap_components as dbc
from dash.development.base_component import Component


def init_modal(id: str, title: str, body: list[Component],
               buttons: list[Component], escape: bool = True,
               class_name: str = '') -> Component:
    """Constructs a modal dialog."""
    return dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle(title), close_button=False),
            dbc.ModalBody(body),
            dbc.ModalFooter(buttons),
        ],
        id=id,
        is_open=False,
        keyboard=escape,
        backdrop='static',
        class_name=class_name,
    )
