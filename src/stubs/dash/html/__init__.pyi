"""This module provides the type stubs for the
[html](https://dash.plotly.com/dash-html-components] from Plotly.
"""

from typing import List, Union
from dash import DashComponent
# from dash.development.base_component import DashComponent

ChildrenParamImpl = Union[str, int, float, DashComponent]
ChildrenParam = Union[None, ChildrenParamImpl, List[ChildrenParamImpl],
                      List[DashComponent]]


class Div(DashComponent):
    def __init__(self, children: ChildrenParam = None,
                 id: str = '') -> None: ...


class H1(DashComponent):
    def __init__(self, children: ChildrenParam = None) -> None: ...


class H2(DashComponent):
    def __init__(self, children: ChildrenParam = None) -> None: ...


class Li(DashComponent):
    def __init__(self, children: ChildrenParam = None) -> None: ...


class P(DashComponent):
    def __init__(self, children: ChildrenParam = None) -> None: ...


class Strong(DashComponent):
    def __init__(self, children: ChildrenParam = None) -> None: ...


class Ul(DashComponent):
    def __init__(self, children: ChildrenParam = None,
                 className: str = '') -> None: ...
