from dash import dcc

# flags
conf_dialog_flag = dcc.Store(id='conf-dialog-flag', data=False)
upload_dialog_flag = dcc.Store(id='upload-dialog-flag', data=False)

# collections
datasets = dcc.Store(id='datasets', data={})  # Dict[Filename, Dataset]

# intermediaries
uploaded_file = dcc.Store(id='uploaded-file')
