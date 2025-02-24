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
    sheet_columns: Dict[SheetName, List[str]],
) -> Dict[SheetName, List[str]]:
    result = {}
    for sheet, table, in sheet_tables.items():
        if not table:
            continue
        result[table] = sheet_columns[sheet]
    return result


def _get_sizes(
    sheet_tables: Dict[SheetName, odm.TableName],
    sheet_rowcounts: Dict[str, int],
) -> Dict[odm.TableName, int]:
    result = {}
    for sheet, table, in sheet_tables.items():
        if table:
            result[table] = sheet_rowcounts[sheet]
    return result


def update_dataset_mapping(ds: Dataset, mapping: Dict[SheetName, odm.TableName]
                           ) -> None:
    columns = ds['sheet_columns']
    rowcounts = ds['sheet_rowcounts']
    ds['table_headers'] = _get_headers(mapping, columns)
    ds['table_sizes'] = _get_sizes(mapping, rowcounts)
    ds['sheet_tables'] = mapping


def import_dataset(filename: Filename, sheets: Dict[SheetName, pd.DataFrame]
                   ) -> Dataset:
    """Constructs a Dataset with data parsed from an Excel/CSV file. May throw
    an exceptionjif the file can't be imported."""
    sheet_names = list(sheets.keys())
    odm_version = odm.infer_version(sheet_names)
    sheet_tables = odm.infer_table_mapping(sheet_names, odm_version)
    sheet_columns = {sheet: list(df.keys()) for sheet, df in sheets.items()}
    sheet_rowcounts = {sheet: len(df) for sheet, df in sheets.items()}
    ds = Dataset(
        filename=filename,
        odm_version=odm_version.value,
        upload_time=datetime.now(),
        sheet_columns=sheet_columns,
        sheet_rowcounts=sheet_rowcounts,
        sheet_tables={},
        table_headers={},
        table_sizes={},
        revision=1,
        valid=None,
    )
    update_dataset_mapping(ds, sheet_tables)
    return ds
