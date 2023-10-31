"""This module provides the type stubs for the 
[html](https://dash.plotly.com/dash-html-components] from Plotly.
"""

from typing import List, Union, Optional
from dash import DashComponent

ChildrenParam = Union[str, int, float, DashComponent, List[DashComponent]]
 
def Div(
    children: Optional[ChildrenParam] = None, 
    id: Optional[str] = None
) -> DashComponent: ...

def Li(children: ChildrenParam) -> DashComponent: ...

def Ul(children: ChildrenParam) -> DashComponent: ...

def H1(children: ChildrenParam) -> DashComponent: ...

def H2(children: ChildrenParam) -> DashComponent: ...

def P(children: ChildrenParam) -> DashComponent: ...

def Strong(children: ChildrenParam) -> DashComponent: ...

