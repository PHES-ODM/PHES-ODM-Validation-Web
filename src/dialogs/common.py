from dash import (
    Input,
    Output,
    no_update,
)


def register_dialog_flag_callback(  # type: ignore
    app,
    dialog_layout,
    flag_store,
    init_store,
):
    @app.callback(
        [
            Output(dialog_layout, 'is_open'),
            Output(init_store, 'data'),
        ],
        Input(flag_store, 'data'),
    )
    def on_dialog_flag(flag: bool) -> tuple[bool, bool]:
        '''open/close dialog'''
        return flag, (True if flag else no_update)
    return on_dialog_flag
