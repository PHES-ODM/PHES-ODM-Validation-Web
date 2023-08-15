# This file explores the following concepts:
# * How to create a custom component in Plotly using a function
# * How two different component can communicate with each other using a 
#   dcc.store as the intermediary
# * Using objects in stores
from dash import Dash, html, dcc, callback, Output, Input, State

# This is out custom component which is simply a Plotly ConfirmDialog 
# Its public API is exposed as a dcc.store whose data is a dictionary with one
# field called is_open. This field controls whether the dialog or closed.
# The function will return an array with two items:
# 1. The confirmation dialog
# 2. The store that other components in the app can change to update the dialog
def confirm_dialog():
    confirm_dialog = dcc.ConfirmDialog(
        id = 'confirm-dialog',
        message = 'Confirmation Dialog', 
        displayed = False
    )

    store = dcc.Store(id = 'confirm-dialog-store', data = {"is_open": False})
    
    @callback(
        Output(store, 'data', allow_duplicate = True),
        Input(confirm_dialog, 'submit_n_clicks'),
        Input(confirm_dialog, 'cancel_n_clicks'),
        State(store, 'data'),
        prevent_initial_call = True
    )
    # Whenever the user clicks on the submit or cancel buttons in the confirm 
    # dialog, the dialog us automatically closed. This callback updates the 
    # store also.
    def on_confirm_dialog_buttons_clicked(
        submit_n_clicks, 
        cancel_n_clicks, 
        data
    ):
        if submit_n_clicks is not None or cancel_n_clicks is not None:
            if submit_n_clicks != 0 or cancel_n_clicks != 0:
                data['is_open'] = False 
        return data

    @callback(
        Output(confirm_dialog, 'displayed'),
        Input(store, 'data'),
    )
    # Closes or opens the dialog based on the store's is_open field.
    def on_confirm_dialog_store_change(data):
       return data["is_open"] 

    return [
        confirm_dialog,
        store
    ]
[test_confirm_dialog, test_confirm_dialog_store] = confirm_dialog()

open_confirm_dialog_button = html.Button(
    id = 'open-confirm-dialog',
    children = 'Open Confirm Dialog'
)
@callback(
    # Whenever a store is an Output, allow_duplicate should be true. This will 
    # allow multiple components to change the store, i.e., multiple components 
    # can communicate with the confirmation dialog component.
    # Use direct reference to components in a callback to avoid dealing with 
    # IDs
    Output(test_confirm_dialog_store, 'data', allow_duplicate = True),
    Input(open_confirm_dialog_button, 'n_clicks'),
    State(test_confirm_dialog_store, 'data'),
    prevent_initial_call=True
)
def on_open_confirm_dialog_click(n_clicks, data): 
    if n_clicks != 0 and n_clicks is not None:
        data["is_open"] = True 
    return data

app = Dash(__name__)
app.layout = html.Div([
    open_confirm_dialog_button,
    test_confirm_dialog,
    test_confirm_dialog_store
])

app.run(debug = True)
