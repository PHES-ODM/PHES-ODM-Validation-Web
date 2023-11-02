from typing import Dict, List

from .odm_defs import (
    TableName,
    Version,
)
from .odm_schemas import get_table_names


def _match(sheet_name: str, table_name: TableName) -> bool:
    """Returns true if `sheet_name` matches `table_name`."""
    return (sheet_name == table_name or
            sheet_name.endswith(' ' + table_name))


def infer_version(sheet_names: List[str]) -> Version:
    """Returns the latest version that matches any of the `sheet_names`.
    Defaults to the latest version."""
    for version in reversed(Version):
        tables = get_table_names(version)
        for table in tables:
            for sheet in sheet_names:
                if _match(sheet, table):
                    return version
    return list(Version)[-1]


def _validate_table_mapping(
    mapping: dict,
    odm_table_names: set[TableName],
    version: Version,
) -> None:
    for table in mapping.values():
        if table and table not in odm_table_names:
            assert (f'"{table}" is not a valid table ' +
                    f'in ODM version {version}')


def infer_table_mapping(sheet_names: List[str], odm_version: Version
                        ) -> Dict[str, TableName]:
    """Attempts to map sheet names to ODM table names."""
    result = {}
    tables = set(get_table_names(odm_version))
    for sheet in sheet_names:
        result[sheet] = ''
        for table in tables:
            if _match(sheet, table):
                result[sheet] = table
                tables.remove(table)
                break
    _validate_table_mapping(result, tables, odm_version)
    return result
