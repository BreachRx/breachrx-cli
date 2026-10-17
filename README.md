# BreachRx CLI

## About
The [BreachRx](https://breachrx.com) command line interface is a utility for power users to streamline their use of the BreachRx incident response management platform and further empower teams to prepare for and get ahead of incidents so they can act decisively when they occur.

## Download
On the releases page, click on Assets at the bottom of the most recent release to download the latest version.

## Usage
Requires Python 3.9 or newer.

```bash
Usage: python breachrx-cli.pyz [OPTIONS] COMMAND [ARGS]...

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  create-incident          Create an Incident and print it as JSON.
  get-incident-severities  List incident severities.
  get-incident-states      List incident states.
  get-incident-types       List incident types.
  list-playbooks           List approved playbook names.
  ping                     Check the setup and print the API version.
  schema                   Show the organization's schema.
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

# Optional. Available to Admins on the Technologies > API Guides page.
BREACHRX_GRAPHQL_URL="<GRAPHQL_ENDPOINT>"
```

Run `python breachrx-cli.pyz ping` to check the setup. It prints the API version.

# Commands

## create-incident
Creates an Incident and prints it as JSON, including a `url` link to it in the platform.

```bash
Usage: python breachrx-cli.pyz create-incident [OPTIONS] INCIDENT_NAME

Options:
  --description TEXT              A brief description of the Incident.
  --custom-identifier TEXT        An optional custom identifier for the
                                  Incident, e.g. a ticket number.
  --severity TEXT                 Incident severity. Defaults to Unknown
                                  unless --playbook is given.
  --incident-type TEXT            Incident type. Repeatable. Defaults to Other
                                  unless --playbook is given.
  --tag TEXT                      Tag. Repeatable.
  --attr 'FIELD=VALUE'            Attribute value. Repeatable. JSON values are
                                  allowed, e.g. --attr 'Country=["US","CA"]'.
  --playbook TEXT                 Name of a playbook to create the Incident
                                  from.
  --merge-strategy [merge|error]  How to resolve conflicts with playbook
                                  values. Defaults to merge.
  --exercise                      Create an Exercise (tabletop, drill, etc.).
  --create-actions / --no-create-actions
                                  Create Actions for the Incident. Defaults to
                                  on.
  --help                          Show this message and exit.
```

Examples:
```bash
python breachrx-cli.pyz create-incident "Ransomware Incident" \
  --severity High --incident-type Ransomware --tag leadership-escalation \
  --attr "Number of Records Impacted=5000" --attr 'Country=["US","CA"]' \
  --custom-identifier TICKET-12345

python breachrx-cli.pyz create-incident "Ransomware Incident" --playbook "Ransomware Response Plan"

python breachrx-cli.pyz create-incident "Tabletop Exercise - Q3" --severity Low --incident-type Ransomware --exercise
```

Attribute values are parsed as JSON when possible; anything else is sent as text, and multiple values can also be pipe-delimited (`"Country=US|CA"`). Use `schema --section conditions` to see the available attribute fields and their options.

## list-playbooks
Prints approved playbook names, one per line and sorted by name, for use with `create-incident --playbook`.
```bash
Usage: python breachrx-cli.pyz list-playbooks [OPTIONS]
```

## schema
```bash
Usage: python breachrx-cli.pyz schema [OPTIONS]

Options:
  --section TEXT  Only show one section, e.g. severities, states, types, tags,
                  conditions.
  --help          Show this message and exit.
```

Without `--section` the full schema is printed as JSON. Sections that are plain lists print one value per line.

## get-incident-severities / get-incident-states / get-incident-types
```bash
Usage: python breachrx-cli.pyz get-incident-types [OPTIONS]
```

## ping
```bash
Usage: python breachrx-cli.pyz ping [OPTIONS]
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
The dependencies are pure Python, so the resulting file runs on any platform with Python 3.9+.
Note: The environment variables must be set.

### GraphQL API
The BreachRx GraphQL API documentation can be found on the Help Guides > API page in the platform.