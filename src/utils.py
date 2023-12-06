import sys
from urllib.parse import quote, unquote
from typing import Any, List


def echo(x: Any) -> None:  # type: ignore
    """Helper that prints to stderr, to help with echo-debugging while using
    Plotly Dash since stdout isn't printed to console."""
    print(x, file=sys.stderr)


def duplicates(a: list) -> list:
    seen = set()
    result = []
    for x in a:
        if x in seen:
            result.append(x)
        else:
            seen.add(x)
    return result


def quoted(s: str) -> str:
    return f'"{s}"'


def get_dataset_path(filename: str) -> str:
    return quote(f'/datasets/{filename}')


def get_pathname_parts(pathname: str) -> List[str]:
    return unquote(pathname).split('/')[1:]


def get_dataset_id(pathname: str) -> str:
    '''returns dataset id from url path, or empty string when not found'''
    parts = get_pathname_parts(pathname)
    if parts[0] != 'datasets':
        return ''
    return parts[1]
