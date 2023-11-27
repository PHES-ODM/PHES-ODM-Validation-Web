"""This module provides the type stubs for the
[html](https://dash.plotly.com/dash-html-components] from Plotly.
"""

from typing import List, Union
from dash.development.base_component import Component

ChildrenParamImpl = Union[str, int, float, Component]
ChildrenParam = Union[None, ChildrenParamImpl, List[ChildrenParamImpl],
                      List[Component]]


class Div(Component):
    def __init__(self, children: ChildrenParam = None,
                 id: str = '') -> None: ...


class H1(Component):
    def __init__(self, children: ChildrenParam = None) -> None: ...


class H2(Component):
    def __init__(self, children: ChildrenParam = None) -> None: ...


class Li(Component):
    def __init__(self, children: ChildrenParam = None) -> None: ...


class P(Component):
    def __init__(self, children: ChildrenParam = None) -> None: ...


class Span(Component):
    def __init__(self, children: ChildrenParam = None) -> None: ...


class Strong(Component):
    def __init__(self, children: ChildrenParam = None) -> None: ...


class Ul(Component):
    def __init__(self, children: ChildrenParam = None,
                 className: str = '') -> None: ...
