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

## Standalone installation

The app can also be packaged as a binary distributable.

1. Pre-built binaries are available in the release section of the github
   repository. If you want to build it yourself, then use the following command
   for your system to package the app:

    Linux:

    `python install/setup.py bdist_appimage`

    Mac:

    `python3 install/setup.py bdist_dmg` or `install/build-mac.sh`

    Windows:

    `python install/setup.py bdist_msi`

2. Distribute and run it. A browser tab pointing to the web-service will be
   opened automatically when running it.

See [mac-dist.md](docs/mac-dist.md)/[win-dist.md](docs/win-dist.md) for more
detailed instructions on how to run it on Mac and Windows respectively.

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
