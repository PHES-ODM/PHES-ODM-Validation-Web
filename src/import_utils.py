import io
import os
import pandas as pd
import warnings
from datetime import datetime
from typing import Dict, List
# from pprint import pprint

from odm import odm
from stores import Dataset, Filename, SheetName

TableRow = dict  # key-value pairs
TableData = List[TableRow]


def _to_dict_list(df: pd.DataFrame) -> List[dict]:
    """converts a pandas DataFrame to a list of dicts with column names as
    keys and field values as values"""
    return df.to_dict('records')


def load_sheets(filename: Filename, data: bytes
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
            dfs = pd.read_excel(io.BytesIO(data), sheet_name=None,
                                na_filter=False)
            return {name: _to_dict_list(df) for (name, df) in dfs.items()}
    else:
        assert False, 'invalid ext'


def get_table_headers(
    sheet_tables: Dict[SheetName, odm.TableName],
    sheet_data: Dict[SheetName, list],
) -> Dict[SheetName, List[str]]:
    result = {}
    for sheet, table, in sheet_tables.items():
        if not table:
            continue
        rows = sheet_data[sheet]
        result[table] = list(rows[0].keys()) if len(rows) > 0 else []
    return result


def get_table_sizes(
    sheet_tables: Dict[SheetName, odm.TableName],
    sheet_data: Dict[str, list]
) -> Dict[odm.TableName, int]:
    result = {}
    for sheet, table, in sheet_tables.items():
        if table:
            result[table] = len(sheet_data[sheet])
    return result


def import_dataset(filename: Filename, sheets: dict) -> Dataset:
    """Constructs a Dataset with data parsed from an Excel/CSV file. May throw
    an exceptionjif the file can't be imported."""
    sheet_names = list(sheets.keys())
    odm_version = odm.infer_version(sheet_names)
    sheet_tables = odm.infer_table_mapping(sheet_names, odm_version)
    headers = get_table_headers(sheet_tables, sheets)
    sizes = get_table_sizes(sheet_tables, sheets)
    return Dataset(
        filename=filename,
        odm_version=odm_version.value,
        upload_time=datetime.now(),
        sheet_tables=sheet_tables,
        table_headers=headers,
        table_sizes=sizes,
        revision=1,
    )
