from typing import Dict
import os
import tempfile

import diskcache
from dash import DiskcacheManager, dcc
from typing_extensions import TypedDict

from dataset_import import Filename, Dataset

DatasetDict = Dict[Filename, Dataset]


class Validation(TypedDict):
    name: str
    summary: str
    report: str


class ValidationSetup(TypedDict):
    dataset_id: str
    validation_name: str
    profile_id: str


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
validation_dialog_flag = dcc.Store(id='validation-dialog-flag', data=False)
progress_dialog_flag = dcc.Store(id='validation-prog-dialog-flag', data=False)

# collections
#

datasets = dcc.Store(id='datasets', data={})
validations = dcc.Store(id='validations', data={})

# intermediaries
#

cancel_operation = dcc.Store(id='cancel-op', data=False)
dataset_conf_form = dcc.Store(id='dataset-conf-form', data={})
dataset_id = dcc.Store(id='dataset-id')
replace_on_dup = dcc.Store(id='replace-on-dup', data=True)
uploaded_file = dcc.Store(id='uploaded-file')
validation_setup = dcc.Store(id='validation-setup')

# other
#

validation_trigger = dcc.Store(id='validation-trigger')

# caching
#

_tmpdir = tempfile.gettempdir()
_tmppath = os.path.join(_tmpdir, 'odm-validation-webtool-cache.dat')
background_callback_manager = DiskcacheManager(diskcache.Cache(_tmppath))
