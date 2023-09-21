import dash_bootstrap_components as dbc


def init_modal(id, title, body, buttons, escape=True):
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
    )
