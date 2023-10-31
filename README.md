# PHES-ODM-Validation-web

This repo contains the code and documentation for the PHES-ODM web validation
tool.

## Project Structure

- [docs/](./docs): The docs folder contains all the documentation for the
  project
- [src/](./src): The src folder contains all the source code for the project.

## Running

First install the dependencies by running the commands in the
[development](#development) section.

For Unix type systems use the command below,

```
.env/bin/python src/app.py
```

For Windows systems use the command below,

```
".env/Scripts/python" src/app.py
```

## Development

For Unix type systems use the commands below,

```
git clone <repo-url> webtool
cd webtool
python -m venv .env
.env/bin/pip install -r requirements.txt
```

For Windows systems replace the last command with,

```
".env/Scripts/pip" install -r requirements.txt
```

## Typing

[mypy](https://mypy.readthedocs.io/en/stable/index.html) is used to perform
type checking on the project. Although Python provides support for adding types,
it does not enforce them at run time nor does it provide a way to statically
analyze them at "compile time". Instead other static analyzer tools like mypy,
Pyright, and PyType have to be used.

Use the command `mypy` to run the type checker.

[A configuration file](./mypy.ini) is used to inform the type checker.

Since types were not added to the project from the start currently only new
files added to the project are type-checked. Every new file added to the
project will need to be added to the `files` option in the mypy configuration
file.

The new file may depend on other modules that will need to be type checked. For
now if the dependent is not a new file, they can be ignored by adding an entry
for them in the configuration file and using the `ignore_missing_import`
option. For example, if the module name is stores, the following entry should
be added,

```
[mypy-stores.*]
ignore_missing_imports = True
```

A major issue with typing in this project is the heavy dependence on Plotly
which does not have any typing or type stubs. The project should aim to add
type stubs for the library pragmatically, since it may not be possible or
too convoluted to add types for some of the Plotly constructs. The type stubs
for Plotly are in the [stubs](./src/stubs/dash/) directory.

Another item with type stubs are types that exist at compile time but not at
run time. For example, the `DashComponent` class which does not exist in Plotly
but is used in the type stubs to type out functions that return an HTML element
like `H1` and `Li`.

Importing these types requires two pieces of code added to ensure that the app
does not fail to run but can also be type checked using mypy,

1. A `from __future__ import annotations` line.
2. An if statement to conditionally import these types if the app is being
   type checked but not run. This is done using the `TYPE_CHECKING` flag from the
   `typing` module in Python.

Putting this together, the code to import such types using `DashComponent` as
an example is shown below,

```{python}
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from dash import DashComponent
```
