import sys
from urllib.parse import quote


def echo(x):
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
    return f'/datasets/{quote(filename)}'
