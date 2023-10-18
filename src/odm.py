import inspect
import os
import tempfile
import yaml
from enum import Enum
from logging import info
from os.path import isfile
from typing import Dict, List
# from pprint import pprint

import odm_validation

TableName = str


class Version(Enum):
    V1_0_0 = 'v1.0.0'
    V1_1_0 = 'v1.1.0'
    V2_0_0 = 'v2.0.0'


_CACHE_DIR = os.path.join(tempfile.gettempdir(), 'odm-tables')
_TABLE_NAMES: Dict[Version, List[TableName]] = {}


def _get_table_cache_path(version: Version) -> str:
    return os.path.join(_CACHE_DIR, version.value) + '.txt'


def _get_file_paths(dir: str) -> List[str]:
    """returns the list of file paths in `dir`"""
    with os.scandir(dir) as entries:
        files = filter(lambda e: e.is_file, entries)
        paths = map(lambda e: os.path.join(dir, e.name), files)
        return list(paths)


def _get_schema_paths() -> List[str]:
    """returns a list of odm-validation schema file paths"""
    mod_path = inspect.getfile(odm_validation)
    mod_dir = os.path.dirname(mod_path)
    asset_dir = os.path.join(mod_dir, 'assets', 'validation-schemas')
    return _get_file_paths(asset_dir)


def _save_table_names(odm_table_names: dict):
    """saves the odm version-table mapping to a text file, using version as
    filename, and storing one table name per line"""
    os.makedirs(_CACHE_DIR, exist_ok=True)
    for version, tables in odm_table_names.items():
        path = _get_table_cache_path(version)
        with open(path, 'w') as f:
            f.write('\n'.join(tables))


def _load_table_names():
    """loades the odm version-table mapping from a cached text file"""
    result = {}
    for path in _get_file_paths(_CACHE_DIR):
        (_, filename) = os.path.split(path)
        (version_str, _) = os.path.splitext(filename)
        version = Version(version_str)
        with open(path) as f:
            tables = f.read().splitlines()
            result[version] = tables
    return result


def _is_cached() -> bool:
    """returns true if all ODM version-table mapping files exist (meaning that
    they are cached)"""
    paths = map(lambda v: _get_table_cache_path(v), Version)
    return all(map(lambda path: isfile(path), paths))


def _extract_table_names(schema_paths: List[str]):
    """returns ODM table names, by version"""
    result = {}
    for path in schema_paths:
        with open(path) as f:
            schema = yaml.load(f, Loader=yaml.Loader)
            tables = list(schema['schema'].keys())
            version_str = 'v' + schema['schemaVersion']
            version = Version(version_str)
            result[version] = tables
    return result


def _init():
    """initializes static module assets"""
    global _TABLE_NAMES
    if _is_cached():
        info('loading odm table names')
        _TABLE_NAMES = _load_table_names()
    else:
        info('extracting odm tables names')
        paths = _get_schema_paths()
        _TABLE_NAMES = _extract_table_names(paths)
        info('caching odm table names')
        _save_table_names(_TABLE_NAMES)


def get_table_names(version: Version) -> List[TableName]:
    return _TABLE_NAMES[version]


_init()
