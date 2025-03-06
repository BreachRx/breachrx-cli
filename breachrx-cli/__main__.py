import click
from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
from gql.transport.exceptions import TransportQueryError
from dotenv import load_dotenv
from aiohttp import BasicAuth
import os
from __init__ import __version__

load_dotenv()

api_key = os.getenv("BREACHRX_API_KEY")
secret_key = os.getenv("BREACHRX_SECRET_KEY")
graphql_url = os.getenv("BREACHRX_GRAPHQL_URL", default="https://graphql.app.breachrx.io/graphql")
orgname = os.getenv("BREACHRX_ORG_NAME")

def execute_query(query, variables=None):
  if not api_key:
    raise Exception("BREACHRX_API_KEY environment variable not set.")
  if not secret_key:
    raise Exception("BREACHRX_SECRET_KEY environment variable not set.")
  if not orgname:
    raise Exception("BREACHRX_ORG_NAME environment variable not set.")
    
  auth = BasicAuth(api_key, secret_key)

  transport = AIOHTTPTransport(
    url=graphql_url,
    auth=auth,
    headers={"orgname": orgname},
    timeout=60
  )
  
  client = Client(
    transport=transport, fetch_schema_from_transport=True
  )

  try: 
    result = client.execute(query, variable_values=variables)
  except TransportQueryError as e:
    return e.errors[0]["message"]
  except Exception as e:
    return str(e)
  else:
    return result

@click.group()
@click.version_option(version=__version__, prog_name="breachrx-cli")
def cli():
  pass

@cli.command()
@click.argument("incident_name")
@click.option("--description", help="A brief description of the Incident.")
@click.option("--custom-identifier", help="An optional custom identifier for the Incident.")
@click.option("--severity", default="Unknown", help="Incident severity.")
@click.option("--state", help="The starting state for the incident. Optional, defaults to Draft.")
@click.option("--incident-type", default="Other", help="Incident type.")
def create_incident(incident_name, description, custom_identifier, severity, state, incident_type):
  mutation = gql("""
  mutation CreateIncident(
    $name: String!,
    $description: String,
    $customIdentifier: String,
    $severity: String!,
    $state: String,
    $type: String!
  ) {
    createIncident(
      name: $name,
      description: $description,
      customIdentifier: $customIdentifier,
      severity: $severity, 
      state: $state,
      type: $type,
    ) {
      id
      name
      description
      customIdentifier
      state
      severity {
        name
      }
      types {
        type {
          name
        }
      }
    }
  }""")

  params = {
    "name": incident_name,
    "description": description,
    "customIdentifier": custom_identifier,
    "severity": severity,
    "state": state,
    "type": incident_type,
  }

  click.echo(execute_query(mutation, params))

@cli.command()
def get_incident_severities():
  query = gql("""{
    incidentSeverities {
      name
		  ordering
    }
  }""")
  severities = execute_query(query)

  for severity in severities["incidentSeverities"]:
    click.echo(severity["name"])

@cli.command()
def get_incident_states():
  query = gql("""{
    state: __type(name: "State") {
      name
      enumValues {
        name
      }
    }
  }""")

  incident_states = execute_query(query)

  for incident_state in incident_states["state"]["enumValues"]:
    click.echo(incident_state["name"])

@cli.command()
def get_incident_types():
  query = gql("""{
    types {
      name
    }
  }""")

  incident_types = execute_query(query)

  for incident_type in incident_types["types"]:
    click.echo(incident_type["name"])

if __name__ == "__main__":
  cli(prog_name="python breachrx-cli.pyz")