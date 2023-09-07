from typing import Dict, List
from enum import Enum

from typing_extensions import TypedDict

OdmTableName = str
TableData = List[dict]
SheetName = str


class OdmVersion(Enum):
    V1_0_0 = 'v1.0.0'
    V1_1_0 = 'v1.1.0'
    V2_0_0 = 'v2.0.0'


class Dataset(TypedDict):
    filename: str
    odm_version: str
    table_names: Dict[SheetName, OdmTableName]
    tables: Dict[OdmTableName, TableData]


def _infer_odm_version(sheet_names) -> OdmVersion:
    # TODO
    return OdmVersion.V2_0_0


def _infer_table_mapping(sheet_names) -> Dict[SheetName, OdmTableName]:
    # TODO
    return {}


def _get_sheet_names(filename, contents) -> List[str]:
    # TODO
    return []


def _import_table_data(contents) -> Dict[OdmTableName, TableData]:
    # TODO
    return {}


def import_dataset(filename, contents) -> Dataset:
    """Constructs a Dataset with data parsed from an Excel/CSV file."""
    sheet_names = _get_sheet_names(filename, contents)
    table_mapping = _infer_table_mapping(sheet_names)
    odm_table_names = list(table_mapping.values())
    return Dataset(
        filename=filename,
        odm_version=str(_infer_odm_version(odm_table_names)),
        table_names=table_mapping,
        tables=_import_table_data(contents),
    )
