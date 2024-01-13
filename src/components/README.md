All the modules in this folder contain the code for a specific UI component.

# Writing a UI component

This section goes over the standard that should be followed when writing a UI
component. There are two standards, one for reusable and one for non-reusable
components.

## Reusable UI Components

These are UI components that are used as a building block in other UI
components. For example the Modal component in the [modals.py](./modals.py)
module which is used to construct the dialogs in the `/src/dialogs/` directory.

Modules that implement such a component should have one public function that
customizes the component and returns it.

## Non-Reusable UI Components

These are UI components that are meant to be used directly in the app. For
example, the [upload dataset dialog](./upload_dialogs.py). Modules that define
these type of components should contain two public variables:

1. A variable which contains the UI component.
2. A function called `register` that takes one argument which is a Dash app.
Within this function all the callbacks for the component should be implemented
using the `@app.callback` decorator. This allows the component to use the app
wide configuration options for its callbacks, making things DRY.
