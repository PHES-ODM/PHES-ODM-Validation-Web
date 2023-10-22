from typing import Union, Callable, Any

# A dash component is what is returned when calling one of the functions 
# to create an [HTML Component](https://dash.plotly.com/dash-html-components),
# a [core component](https://dash.plotly.com/dash-core-components), or even 
# a custom component.
class DashComponent:
    pass

# The type alias for the component_id parameter for any of the entities used 
# when creating a callback for example an Output.
ComponentParam = Union[str, DashComponent]

class DashInput:
    pass
def Input(
    component_id: ComponentParam, 
    component_property: str
) -> DashInput: ...

class DashOutput:
    pass
def Output(
    component_id: ComponentParam, 
    component_property: str
) -> DashOutput: ...

class DashState:
    pass
def State(
    component_id: ComponentParam, 
    component_property: str
) -> DashState: ...

class DashApp:
    def callback(
        self: 'DashApp',
        *args: Union[DashInput, DashOutput, DashState],
        prevent_initial_call: bool
    ) -> Callable: ...

def callback(
    *args: Union[DashInput, DashOutput, DashState],
    prevent_initial_call: bool = False
) -> Callable: ... 

# A no_update can be returned in place of any Output in a callback. This makes 
# it hard to type since it should be equal to the type of any Output of a 
# callback which is impossible. Set it to Any and ignore it for now.
no_update: Any # type: ignore 

def register_page(module: str, path_template: str) -> None: ...

