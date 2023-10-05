# PHES-ODM-Validation-web

This repo contains the code and documentation for the PHES-ODM web validation
tool.

## Project Structure

* [docs/](./docs): The docs folder contains all the documentation for the
  project
* [src/](./src): The src folder contains all the source code for the project.

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
