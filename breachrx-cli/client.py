import base64
import json
import os
import urllib.error
import urllib.request

import click
from dotenv import find_dotenv, load_dotenv
from __init__ import __version__

load_dotenv(find_dotenv(usecwd=True))

api_key = os.getenv("BREACHRX_API_KEY")
secret_key = os.getenv("BREACHRX_SECRET_KEY")
graphql_url = os.getenv("BREACHRX_GRAPHQL_URL", default="https://graphql.app.breachrx.io/graphql")
orgname = os.getenv("BREACHRX_ORG_NAME")

def execute_query(query, variables=None):
  if not api_key:
    raise click.ClickException("BREACHRX_API_KEY environment variable not set.")
  if not secret_key:
    raise click.ClickException("BREACHRX_SECRET_KEY environment variable not set.")
  if not orgname:
    raise click.ClickException("BREACHRX_ORG_NAME environment variable not set.")

  auth = base64.b64encode(f"{api_key}:{secret_key}".encode()).decode()
  request = urllib.request.Request(
    graphql_url,
    data=json.dumps({"query": query, "variables": variables or {}}).encode(),
    headers={
      "Content-Type": "application/json",
      "Authorization": f"Basic {auth}",
      "orgName": orgname,
      "User-Agent": f"breachrx-cli/{__version__}",
    },
    method="POST",
  )

  status = None
  try:
    with urllib.request.urlopen(request, timeout=60) as response:
      body = response.read()
  except urllib.error.HTTPError as e:
    status = f"HTTP {e.code} {e.reason}"
    body = e.read()
    if not body:
      raise click.ClickException(status)
  except urllib.error.URLError as e:
    raise click.ClickException(f"Unable to reach {graphql_url}: {e.reason}")

  try:
    result = json.loads(body)
  except ValueError:
    result = None

  if isinstance(result, dict) and result.get("errors"):
    messages = (error.get("message", str(error)) for error in result["errors"])
    raise click.ClickException("; ".join(messages))

  if not isinstance(result, dict) or not result.get("data"):
    detail = result.get("message") if isinstance(result, dict) else None
    detail = detail or body[:200].decode(errors="replace")
    prefix = f"{status} from" if status else "Unexpected response from"
    raise click.ClickException(f"{prefix} {graphql_url}: {detail}")

  return result["data"]

def parse_attributes(attrs):
  attributes = []
  for attr in attrs:
    field, sep, value = attr.partition("=")
    if not sep or not field.strip():
      raise click.BadParameter(
        f"'{attr}' must be in the form 'Field Name=value'.", param_hint="--attr"
      )
    try:
      value = json.loads(value)
    except ValueError:
      pass
    attributes.append({field.strip(): value})
  return attributes

def build_variables(**kwargs):
  # Omit unset options so the API only changes what was asked for.
  return {key: value for key, value in kwargs.items() if value is not None and value != ()}
