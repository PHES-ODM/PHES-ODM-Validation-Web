import os
import tempfile
from base64 import b64decode, b64encode
from collections.abc import Generator
from datetime import datetime
from io import BytesIO
from typing import Optional

import diskcache
import pandas as pd
from dash import DiskcacheManager, dcc
from functional import seq
from typing_extensions import TypedDict

from odm import odm

DatasetId = str
Filename = str
SheetName = str


class Dataset(TypedDict):
    '''metadata only'''
    filename: str
    odm_version: str
    upload_time: datetime
    sheet_tables: dict[SheetName, odm.TableName]
    sheet_columns: dict[SheetName, list[str]]
    sheet_rowcounts: dict[SheetName, int]
    revision: int
    valid: Optional[bool]


DatasetDict = dict[Filename, Dataset]


class Validation(TypedDict):
    '''metadata only'''
    name: str
    summary: str
    ds_revision: int


class ValidationSetup(TypedDict):
    dataset_id: str
    validation_name: str
    profile_id: str


def get_table_mapping(
    ds: Dataset
) -> Generator[tuple[SheetName, Optional[odm.TableName]]]:
    # accesses table names in a type-safe way, by converting empty table names
    # to optional ones
    for sheet, table in ds['sheet_tables'].items():
        assert table is not None
        yield (sheet, (table if table != '' else None))


def _get_table_sheet(ds: Dataset, table: str) -> Optional[str]:
    assert table != ''
    for sheet, sheet_table in get_table_mapping(ds):
        if sheet_table == table:
            return sheet
    return None


def get_table_size(ds: Dataset, table: str) -> int:
    sheet = _get_table_sheet(ds, table)
    assert sheet
    return ds['sheet_rowcounts'][sheet]


def get_table_headers(ds: Dataset, table: str) -> list[str]:
    sheet = _get_table_sheet(ds, table)
    assert sheet
    return ds['sheet_columns'][sheet]


def _encode_dataframes(dfs: dict[SheetName, pd.DataFrame]
                       ) -> dict[SheetName, str]:
    '''encodes dataframes as compressed CSV text'''
    result = {}
    for sheet_name, df in dfs.items():
        f = BytesIO()
        df.to_csv(f, index=False)
        content = f.getvalue()
        encoded = b64encode(content).decode('ascii')
        result[sheet_name] = encoded
    return result


def _decode_files(enc: dict[SheetName, str]
                  ) -> dict[SheetName, BytesIO]:
    '''decodes compressed CSV text to file objects'''
    result = {}
    for sheet_name, encoded in enc.items():
        content = b64decode(encoded.encode('ascii'))
        f = BytesIO(content)
        result[sheet_name] = f
    return result


def _decode_csv_df(data: BytesIO) -> pd.DataFrame:
    return pd.read_csv(data, na_filter=False, dtype=str)


def _decode_dataframes(enc: dict[SheetName, str]
                       ) -> dict[SheetName, pd.DataFrame]:
    '''decodes compressed CSV text to dataframes'''
    return seq(_decode_files(enc).items())\
        .map(lambda kv: (kv[0], _decode_csv_df(kv[1])))\
        .dict()


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

# storage type constant for dev. purposes
ST = 'memory'

# dialog flags
#

conf_dialog_flag = dcc.Store(id='conf-dialog-flag', data=False)
progress_dialog_flag = dcc.Store(id='validation-prog-dialog-flag', data=False)
report_dialog_flag = dcc.Store(id='report-dialog-flag', data=False)
share_dialog_flag = dcc.Store(id='share-dialog-flag', data=False)
upload_dialog_flag = dcc.Store(id='upload-dialog-flag', data=False)
validation_dialog_flag = dcc.Store(id='validation-dialog-flag', data=False)

# signals
#

conf_dialog_init = dcc.Store(id='conf-dialog-init', data=False)
share_dialog_init = dcc.Store(id='share-dialog-init', data=False)
share_dialog_share = dcc.Store(id='share-dialog-share', data=False)
progress_dialog_init = dcc.Store(id='progress-dialog-init', data=False)
report_dialog_init = dcc.Store(id='report-dialog-init', data=False)
upload_dialog_init = dcc.Store(id='upload-dialog-init', data=False)
validation_dialog_init = dcc.Store(id='validation-dialog-init', data=False)

# collections
#

dataset_data = dcc.Store(id='dataset-data', data={}, storage_type=ST)
datasets = dcc.Store(id='datasets', data={}, storage_type=ST)
validations = dcc.Store(id='validations', data={}, storage_type=ST)
validation_reports = dcc.Store(id='validation-reports', data={},
                               storage_type=ST)
validation_summaries = dcc.Store(id='validation-summaries', data={},
                                 storage_type=ST)

# intermediaries
#

cancel_operation = dcc.Store(id='cancel-op', data=False)
dataset_conf_form = dcc.Store(id='dataset-conf-form', data={})
dataset_id = dcc.Store(id='dataset-id', storage_type=ST)
replace_on_dup = dcc.Store(id='replace-on-dup', data=True)
uploaded_data = dcc.Store(id='uploaded-data')
uploaded_name = dcc.Store(id='uploaded-name')
validation_setup = dcc.Store(id='validation-setup')

# other
#

validation_trigger = dcc.Store(id='validation-trigger')
sharing_schema_filename = dcc.Store(id='sharing-schema-name', data='',
                                    storage_type=ST)
sharing_schema_data = dcc.Store(id='sharing-schema-content', data='',
                                storage_type=ST)

# caching
#

_tmpdir = tempfile.gettempdir()
_tmppath = os.path.join(_tmpdir, 'odm-validation-webtool-cache.dat')
background_callback_manager = DiskcacheManager(diskcache.Cache(_tmppath))
