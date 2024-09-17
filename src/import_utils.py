import base64
import io
import os
import pandas as pd
import warnings
from datetime import datetime
from typing import Dict, List, Tuple
# from pprint import pprint

from odm import odm
from stores import Dataset, Filename, SheetName

TableRow = dict  # key-value pairs
TableData = List[TableRow]


def decode_contents(contents: str) -> Tuple[str, bytes]:
    '''decode string with file type and base64-encoded file data'''
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    return content_type, decoded


def load_dfs(filename: Filename, data: bytes) -> Dict[SheetName, pd.DataFrame]:
    """returns a dictionary of sheet-names and their respective table data"""
    # XXX: excel warnings are ignored to hide warning about excel
    # data-validation not being supported in pandas/openpyxl
    (name, ext) = os.path.splitext(filename)
    if ext == '.csv':
        df = pd.read_csv(io.StringIO(data.decode('utf-8')))
        return {name: df}
    elif ext == '.xlsx':
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=UserWarning)
            dfs = pd.read_excel(io.BytesIO(data), sheet_name=None,
                                na_filter=False)
            return {name: df for (name, df) in dfs.items()}
    else:
        assert False, 'invalid ext'


def _get_headers(
    sheet_tables: Dict[SheetName, odm.TableName],
    sheet_data: Dict[SheetName, pd.DataFrame],
) -> Dict[SheetName, List[str]]:
    result = {}
    for sheet, table, in sheet_tables.items():
        if not table:
            continue
        df = sheet_data[sheet]
        result[table] = list(df.keys())
    return result


def _get_row_counts(
    sheet_tables: Dict[SheetName, odm.TableName],
    sheet_data: Dict[str, pd.DataFrame],
) -> Dict[odm.TableName, int]:
    result = {}
    for sheet, table, in sheet_tables.items():
        if table:
            result[table] = len(sheet_data[sheet])
    return result


def import_dataset(filename: Filename, sheets: Dict[SheetName, pd.DataFrame]
                   ) -> Dataset:
    """Constructs a Dataset with data parsed from an Excel/CSV file. May throw
    an exceptionjif the file can't be imported."""
    sheet_names = list(sheets.keys())
    odm_version = odm.infer_version(sheet_names)
    sheet_tables = odm.infer_table_mapping(sheet_names, odm_version)
    headers = _get_headers(sheet_tables, sheets)
    sizes = _get_row_counts(sheet_tables, sheets)
    return Dataset(
        filename=filename,
        odm_version=odm_version.value,
        upload_time=datetime.now(),
        sheet_tables=sheet_tables,
        table_headers=headers,
        table_sizes=sizes,
        revision=1,
        valid=None,
    )
