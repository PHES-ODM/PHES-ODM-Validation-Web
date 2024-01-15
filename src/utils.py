import sys
from urllib.parse import quote, unquote
from typing import Any, List, Tuple, Union

from dash import (
    html,
)
from dash.development.base_component import Component


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
    return list(set(result))


def quoted(s: str) -> str:
    return f'"{s}"'


def get_dataset_path(filename: str) -> str:
    return quote(f'/datasets/{filename}')


def get_validation_path(dataset_id: str, validation_name: str) -> str:
    return quote(f'/validations/{dataset_id}/{validation_name}')


def get_pathname_parts(pathname: str) -> List[str]:
    return unquote(pathname).split('/')[1:]


def get_dataset_id(pathname: str) -> str:
    '''returns dataset id from url path, or empty string when not found'''
    parts = get_pathname_parts(pathname)
    if parts[0] != 'datasets':
        return ''
    return parts[1]


def get_validation_id(pathname: str) -> Tuple[str, str]:
    '''validation id is (dataset_id, validation_name)'''
    parts = get_pathname_parts(pathname)
    assert parts[0] == 'validations'
    return (parts[1], parts[2])


def gen_html_list(xs: Union[list, dict]) -> Component:
    if isinstance(xs, list):
        return html.Ul(list(map(html.Li, xs)), className='compact-list')
    elif isinstance(xs, dict):
        items: List[html.Li] = []
        for key, values in xs.items():
            items.append(html.Li([key, gen_html_list(values)]))
        return html.Ul(items)
    assert False
