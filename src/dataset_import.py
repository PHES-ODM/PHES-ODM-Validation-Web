# TODO: move Dataset class to a separate module

import io
import os
import pandas as pd
import warnings
from datetime import datetime
from typing import Dict, List
# from pprint import pprint

from typing_extensions import TypedDict

from odm import odm

Filename = str
SheetName = str
TableRow = dict  # key-value pairs
TableData = List[TableRow]


class Dataset(TypedDict):
    filename: str
    odm_version: str
    upload_time: datetime
    table_mapping: Dict[SheetName, odm.TableName]
    sheets: Dict[SheetName, TableData]


def _to_dict_list(df: pd.DataFrame) -> List[dict]:
    """converts a pandas DataFrame to a list of dicts with column names as
    keys and field values as values"""
    return df.to_dict('records')


def _load_sheets(filename: Filename, data: bytes
                 ) -> Dict[SheetName, TableData]:
    """returns a dictionary of sheet-names mapped to dataframes"""
    # XXX: excel warnings are ignored to hide warning about excel
    # data-validation not being supported in pandas/openpyxl
    (name, ext) = os.path.splitext(filename)
    if ext == '.csv':
        df = pd.read_csv(io.StringIO(data.decode('utf-8')))
        return {name: _to_dict_list(df)}
    elif ext == '.xlsx':
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=UserWarning)
            dfs = pd.read_excel(io.BytesIO(data), sheet_name=None)
            return {name: _to_dict_list(df) for (name, df) in dfs.items()}
    else:
        assert False, 'invalid ext'


def import_dataset(filename: Filename, data: bytes) -> Dataset:
    """Constructs a Dataset with data parsed from an Excel/CSV file. May throw
    an exceptionjif the file can't be imported."""
    sheets = _load_sheets(filename, data)
    sheet_names = list(sheets.keys())
    odm_version = odm.infer_version(sheet_names)
    table_mapping = odm.infer_table_mapping(sheet_names, odm_version)
    return Dataset(
        filename=filename,
        odm_version=odm_version.value,
        upload_time=datetime.now(),
        table_mapping=table_mapping,
        sheets=sheets,
    )
