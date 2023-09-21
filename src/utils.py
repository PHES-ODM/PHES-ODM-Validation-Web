import sys


def echo(x):
    """Helper that prints to stderr, to help with echo-debugging while using
    Plotly Dash since stdout isn't printed to console."""
    print(x, file=sys.stderr)
