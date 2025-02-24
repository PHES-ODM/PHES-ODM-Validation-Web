import logging
import os
import time
import yaml
from typing import List

import odm_validation.utils

from .odm_defs import (
    ColumnName,
    TableName,
    Version,
    TableMetadata,
)

_version_table_columns: TableMetadata


def get_table_names(version: Version) -> List[TableName]:
    return list(_version_table_columns[version.value].keys())


def get_column_names(version: Version, table_name: TableName
                     ) -> List[ColumnName]:
    tables = _version_table_columns[version.value]
    return tables.get(table_name, [])


def _get_file_paths(dir: str) -> List[str]:
    """returns the list of file paths in `dir`"""
    with os.scandir(dir) as entries:
        files = filter(lambda e: e.is_file, entries)
        paths = map(lambda e: os.path.join(dir, e.name), files)
        return list(paths)


def _get_schema_dir() -> str:
    asset_dir = odm_validation.utils.get_asset_dir()
    schema_dir = os.path.join(asset_dir, 'validation-schemas')
    return schema_dir


def _get_schema_paths() -> List[str]:
    """returns a list of odm-validation schema file paths"""
    schema_dir = _get_schema_dir()
    return _get_file_paths(schema_dir)


def _get_tables(schema: dict) -> List[TableName]:
    return list(schema['schema'].keys())


def _get_table_columns(schema: dict, table: TableName) -> List[ColumnName]:
    return list(schema['schema'][table]['schema']['schema'].keys())


def _gen_table_metadata() -> TableMetadata:
    result = {}
    schema_paths = _get_schema_paths()
    for path in schema_paths:
        with open(path) as f:
            schema = yaml.load(f, Loader=yaml.Loader)
            version_str = 'v' + schema['schemaVersion']
            tables = _get_tables(schema)
            table_columns = {}
            for table in tables:
                table_columns[table] = _get_table_columns(schema, table)
            result[version_str] = table_columns
    return result


def load_schema(version: Version) -> dict:
    dir = _get_schema_dir()
    filename = f'schema-{version.value}.yml'
    path = os.path.join(dir, filename)
    with open(path) as f:
        return yaml.load(f, Loader=yaml.Loader)


def init() -> None:
    # TODO: add caching and remove benchmark
    global _version_table_columns
    logging.info('generating ODM table metadata...')
    t0 = time.perf_counter()
    _version_table_columns = _gen_table_metadata()
    t1 = time.perf_counter()
    logging.info(f'gen time: {t1-t0}s')
