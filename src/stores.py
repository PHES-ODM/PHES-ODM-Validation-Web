from typing import Dict

from dash import dcc

from dataset_import import Filename, Dataset

DatasetDict = Dict[Filename, Dataset]


# This adds a third value to the set of dialog-flag values ({False, True}).
# They can all be seen as a super-set of integers which evaluate to either
# False (for 0) or True (for the rest), meaning that they're (backwards)
# compatible with boolean checks at the same time as the actual int value can
# be queried to facilitate special cases.
#
# In the specific case of the conf-dialog-flag, False/0 means closed, True/1
# means opened from somewhere other than upload-dataset dialog, and 2 means
# that it
# was opened from the upload dialog.
OPEN_FROM_UPLOAD: int = 2

# dialog flags
#

conf_dialog_flag = dcc.Store(id='conf-dialog-flag', data=False)
upload_dialog_flag = dcc.Store(id='upload-dialog-flag', data=False)

# collections
#

datasets = dcc.Store(id='datasets', data={})

# intermediaries
#

dataset_conf_form = dcc.Store(id='dataset-conf-form', data={})
dataset_id = dcc.Store(id='dataset-id')
uploaded_file = dcc.Store(id='uploaded-file')
