import io
import os
import pandas as pd
import warnings
from typing import Dict, List
# from pprint import pprint

from typing_extensions import TypedDict

import odm

TableRow = dict  # key-value pairs
TableData = List[TableRow]
SheetName = str


class Dataset(TypedDict):
    filename: str
    odm_version: str
    table_names: Dict[SheetName, odm.TableName]
    tables: Dict[odm.TableName, TableData]


def _match(sheet_name, table_name) -> bool:
    """Returns true if `sheet_name` matches `table_name`."""
    return (sheet_name == table_name or
            sheet_name.endswith(' ' + table_name))


def _infer_odm_version(sheet_names) -> odm.Version:
    """Returns the latest version that matches any of the `sheet_names`.
    Defaults to the latest version."""
    for version in reversed(odm.Version):
        tables = odm.get_table_names(version)
        for table in tables:
            for sheet in sheet_names:
                if _match(sheet, table):
                    return version
    return list(odm.Version)[-1]


def _infer_table_mapping(sheet_names: List[SheetName], odm_version: odm.Version
                         ) -> Dict[SheetName, odm.TableName]:
    """Attempts to map sheet names to ODM table names."""
    result = {}
    tables = set(odm.get_table_names(odm_version))
    for sheet in sheet_names:
        result[sheet] = None
        for table in tables:
            if _match(sheet, table):
                result[sheet] = table
                tables.remove(table)
                break
    return result


def _to_dict_list(df: pd.DataFrame) -> List[dict]:
    """converts a pandas DataFrame to a list of dicts with column names as
    keys and field values as values"""
    return df.to_dict('records')


def _load_sheets(filename, data) -> Dict[SheetName, TableData]:
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


def import_dataset(filename, data) -> Dataset:
    """Constructs a Dataset with data parsed from an Excel/CSV file. May throw
    an exceptionjif the file can't be imported."""
    sheets = _load_sheets(filename, data)
    sheet_names = list(sheets.keys())
    odm_version = _infer_odm_version(sheet_names)
    table_mapping = _infer_table_mapping(sheet_names, odm_version)
    return Dataset(
        filename=filename,
        odm_version=odm_version.value,
        table_names=table_mapping,
        tables=sheets,
    )
