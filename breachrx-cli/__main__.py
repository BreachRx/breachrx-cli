import json

import click
from __init__ import __version__
from client import build_variables, execute_query, parse_attributes

def echo_json(data):
  click.echo(json.dumps(data, indent=2))

@click.group()
@click.version_option(version=__version__, prog_name="breachrx-cli")
def cli():
  pass

@cli.command(short_help="Check the setup and print the API version.")
def ping():
  """Check connectivity and credentials by printing the API version."""
  click.echo(execute_query("{ version }")["version"])

SCHEMA_QUERY = "query GetSchemaForIntegration { getSchemaForIntegration }"

def get_schema_section(section):
  schema = execute_query(SCHEMA_QUERY)["getSchemaForIntegration"]
  if section is None:
    return schema
  if section not in schema:
    raise click.BadParameter(
      f"Unknown section '{section}'. Available: {', '.join(schema.keys())}",
      param_hint="--section",
    )
  return schema[section]

@cli.command(short_help="Show the organization's schema.")
@click.option("--section",
  help="Only show one section, e.g. severities, states, types, tags, conditions.")
def schema(section):
  """Show the organization's schema: severities, states, types, tags, attributes, etc."""
  data = get_schema_section(section)
  if isinstance(data, list) and all(isinstance(item, str) for item in data):
    for item in data:
      click.echo(item)
  else:
    echo_json(data)

@cli.command(short_help="List incident severities.")
def get_incident_severities():
  """List incident severities (same as `schema --section severities`)."""
  for severity in get_schema_section("severities"):
    click.echo(severity)

@cli.command(short_help="List incident states.")
def get_incident_states():
  """List incident states (same as `schema --section states`)."""
  for incident_state in get_schema_section("states"):
    click.echo(incident_state)

@cli.command(short_help="List incident types.")
def get_incident_types():
  """List incident types (same as `schema --section types`)."""
  for incident_type in get_schema_section("types"):
    click.echo(incident_type)

@cli.command(short_help="List approved playbook names.")
def list_playbooks():
  """List approved playbook names, for use with `create-incident --playbook`."""
  query = "query ListPlaybooksForIntegration { listPlaybooksForIntegration(isApproved: true) }"
  names = [playbook["name"] for playbook in execute_query(query)["listPlaybooksForIntegration"]]
  for name in sorted(names, key=str.casefold):
    click.echo(name)

@cli.command(short_help="Create an Incident and print it as JSON.")
@click.argument("incident_name")
@click.option("--description", help="A brief description of the Incident.")
@click.option("--custom-identifier",
  help="An optional custom identifier for the Incident, e.g. a ticket number.")
@click.option("--severity",
  help="Incident severity. Defaults to Unknown unless --playbook is given.")
@click.option("--incident-type", "types", multiple=True,
  help="Incident type. Repeatable. Defaults to Other unless --playbook is given.")
@click.option("--tag", "tags", multiple=True, help="Tag. Repeatable.")
@click.option("--attr", "attrs", multiple=True, metavar="'FIELD=VALUE'",
  help="Attribute value. Repeatable. JSON values are allowed, "
    "e.g. --attr 'Country=[\"US\",\"CA\"]'.")
@click.option("--playbook", help="Name of a playbook to create the Incident from.")
@click.option("--merge-strategy", type=click.Choice(["merge", "error"]),
  help="How to resolve conflicts with playbook values. Defaults to merge.")
@click.option("--exercise", "is_exercise", is_flag=True, default=None,
  help="Create an Exercise (tabletop, drill, etc.).")
@click.option("--create-actions/--no-create-actions", default=None,
  help="Create Actions for the Incident. Defaults to on.")
def create_incident(incident_name, description, custom_identifier, severity, types, tags, attrs,
  playbook, merge_strategy, is_exercise, create_actions):
  """Create an Incident named INCIDENT_NAME."""
  # Without a playbook the API requires severity and types; with one they come from the playbook.
  if not playbook:
    severity = severity or "Unknown"
    types = types or ("Other",)

  mutation = """
  mutation CreateIncidentForIntegration(
    $name: String!
    $description: String
    $customIdentifier: String
    $severity: String
    $types: JSON
    $tags: JSON
    $attributes: JSON
    $createActions: Boolean
    $isExercise: Boolean
    $playbook: String
    $mergeStrategy: String
  ) {
    createIncidentForIntegration(
      name: $name
      description: $description
      customIdentifier: $customIdentifier
      severity: $severity
      types: $types
      tags: $tags
      attributes: $attributes
      createActions: $createActions
      isExercise: $isExercise
      playbook: $playbook
      mergeStrategy: $mergeStrategy
    )
  }"""

  variables = build_variables(
    name=incident_name,
    description=description,
    customIdentifier=custom_identifier,
    severity=severity,
    types=list(types) or None,
    tags=list(tags) or None,
    attributes=parse_attributes(attrs) or None,
    createActions=create_actions,
    isExercise=is_exercise,
    playbook=playbook,
    mergeStrategy=merge_strategy,
  )

  echo_json(execute_query(mutation, variables)["createIncidentForIntegration"])

if __name__ == "__main__":
  cli(prog_name="python breachrx-cli.pyz")
