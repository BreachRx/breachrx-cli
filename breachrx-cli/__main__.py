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
  if api_key == None:
    raise Exception("BREACHRX_API_KEY environment variable not set.")
  elif secret_key == None:
    raise Exception("BREACHRX_SECRET_KEY environment variable not set.")
  elif orgname == None:
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
  else:
    return result

@click.group()
@click.version_option(version=__version__, prog_name="breachrx-cli")
def cli():
  pass

@cli.command()
@click.argument("incident_name")
@click.option("--severity", default="Unknown", help="Incident severity.")
@click.option("--incident-type", default="Other", help="Incident type.")
@click.option("--description", help="A brief description of the Incident.")
def create_incident(incident_name, severity, incident_type, description):
  mutation = gql("""
  mutation CreateIncident(
    $severity: String!,
    $name: String!,
    $type: String!,
    $description: String
  ) {
    createIncident(
      type: $type, 
      severity: $severity, 
      name: $name,
      description: $description
    ) {
      id
      name
      severity {
        name
      }
      types {
        type {
          name
        }
      }
      description
    }
  }""")

  params = {
    "severity": severity,
    "name": incident_name,
    "type": incident_type,
    "description": description
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