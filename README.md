# BreachRx CLI

## About
The [BreachRx](https://breachrx.com) command line interface is a utility for power users to streamline their use of the BreachRx incident management platform and further empower teams to prepare for and get ahead of incidents so they can act decisively when they occur.

## Download
On the releases page, click on Assets at the bottom of the most recent release to download the latest version.

## Usage

```bash
Usage: python breachrx-cli.pyz [OPTIONS] COMMAND [ARGS]...

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  create-incident
  get-incident-severities
  get-incident-types

```

## Setup
Set the following environment variables (or create a [.env](https://pypi.org/project/python-dotenv/) file in the directory you plan to run the command in, with the following variables set):
```bash
# API Key and Secret Key can be generated on the BreachRx platform by an Admin.
BREACHRX_API_KEY="<API_KEY>"
BREACHRX_SECRET_KEY="<API_SECRET_KEY>"

# This corresponds to the simple org name in your organization's custom subdomain used when accessing the BreachRx platform.
# https://<ORG_NAME>.app.breachrx.io
BREACHRX_ORG_NAME="<ORG_NAME>" 
```

# Commands

## create-incident

```bash
Usage: python breachrx-cli.pyz create-incident [OPTIONS] INCIDENT_NAME

Options:
  --severity TEXT       Incident severity.
  --incident-type TEXT  Incident type.
  --description TEXT    A brief description of the Incident.
  --help                Show this message and exit.
```

## get-incident-severities

```bash
Usage: python breachrx-cli.pyz get-incident-severities [OPTIONS]

Options:
  --help  Show this message and exit.
```

## get-incident-types
```bash
Usage: python breachrx-cli.pyz get-incident-types [OPTIONS]

Options:
  --help  Show this message and exit.
```

## Development
Development requires installing Poetry (`pip install poetry`).

```bash
poetry install
poetry self add poetry-plugin-export
```

### How to build a single python executable
```bash
poetry export -f requirements.txt --output requirements.txt --without-hashes
mkdir dist
cp -rf breachrx-cli dist
python -m pip install -r requirements.txt --target dist/breachrx-cli
python -m zipapp -p "/usr/bin/env python3" dist/breachrx-cli
```
The resulting pyz file in the `dist/` directory can be executed with the following command from any directory:
```bash
python breachrx-cli.pyz --help
```
Note: The environment variables must be set.

### GraphQL API
The BreachRx GraphQL API documentation can be found [here](https://www.breachrx.com/docs/breachrx-api/).