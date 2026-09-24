# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
import json
from pathlib import Path
from zoneinfo import ZoneInfo

from a2ui.basic_catalog.provider import BasicCatalog
from a2ui.schema.manager import A2uiSchemaManager
from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.apps import App
from google.adk.code_executors import AgentEngineSandboxCodeExecutor
from google.adk.models import Gemini
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.genai import types

from app.a2ui_utils import a2ui_callback
from app.tools import (
    add_table,
    fetch_data_tool_metadata,
    generate_diagram_image,
    generate_domain_video,
    get_table_details,
    list_tables,
    validate_and_explain_sql,
)

# Load Agent Engine resource name from deployment_metadata.json
metadata_file = Path(__file__).parent.parent / "deployment_metadata.json"
agent_engine_resource_name = None
if metadata_file.exists():
    try:
        with open(metadata_file, "r") as f:
            meta = json.load(f)
            agent_engine_resource_name = meta.get("remote_agent_runtime_id")
    except Exception:
        pass

code_executor = (
    AgentEngineSandboxCodeExecutor(agent_engine_resource_name=agent_engine_resource_name)
    if agent_engine_resource_name
    else AgentEngineSandboxCodeExecutor()
)


# WRITE: after each turn, send the session to Memory Bank for extraction.
async def generate_memories_callback(callback_context: CallbackContext):
    await callback_context.add_session_to_memory()
    return None


def get_weather(query: str) -> str:
    """Simulates a web search. Use it get information on weather.

    Args:
        query: A string containing the location to get weather information for.

    Returns:
        A string with the simulated weather information for the queried location.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        return "It's 60 degrees and foggy."
    return "It's 90 degrees and sunny."


def get_current_time(query: str) -> str:
    """Simulates getting the current time for a city.

    Args:
        city: The name of the city to get the current time for.

    Returns:
        A string with the current time information.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        tz_identifier = "America/Los_Angeles"
    else:
        return f"Sorry, I don't have timezone information for query: {query}."

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    return f"The current time for query {query} is {now.strftime('%Y-%m-%d %H:%M:%S %Z%z')}"


# Build A2UI v0.8 System Prompt using A2uiSchemaManager and BasicCatalog
schema_manager = A2uiSchemaManager(
    version="0.8",
    catalogs=[BasicCatalog.get_config("0.8")],
)

instruction = schema_manager.generate_system_prompt(
    role_description=(
        "You are DataCraft, an expert Data Engineering & SQL Assistant. "
        "You help users manage database schemas, inspect table catalogs, "
        "add new table definitions to the catalog, optimize SQL queries across PostgreSQL, BigQuery, and Snowflake, "
        "and execute Python code in a secure Agent Engine sandbox to compute statistics, schema diffs, or data analysis."
    ),
    workflow_description=(
        "Analyze the user request and return structured A2UI UI cards when appropriate. "
        "Use your Firestore catalog tools (list_tables, get_table_details, add_table) to fetch and record database schema information, "
        "use validate_and_explain_sql to analyze and optimize SQL queries, "
        "use fetch_data_tool_metadata to fetch live stats for open-source data engineering tools, "
        "use generate_diagram_image to create visual architecture or ER diagrams, "
        "and use generate_domain_video to generate animated video visualizations for data pipelines using Gemini Omni."
    ),
    ui_description=(
        "Keep every surface tiny and flat: ONE Card > ONE Column > a few Text rows. "
        "Never nest a Card inside a Card. "
        "Use ONLY these components: Card, Column, Row, Text, and Image. Do not use "
        "Table or Heading (unsupported), or Buttons, actions, or forms (they do "
        "nothing in adk web). "
        "You may include one Image component, but only when you have a public https "
        "URL for the image (for example the URL an image tool returns after uploading "
        "to a public bucket). Set the Image url to that exact https link, for example "
        "{\"Image\": {\"url\": {\"literalString\": \"https://...\"}}}. Never point an "
        "Image at a bare filename, an artifact name, or a non-http(s) path. If you do "
        "not have a public URL, add a short Text line noting the image instead. "
        "No markdown in text; use the usageHint property ('h1', 'h2', 'body') for "
        "headings and emphasis. "
        "Output ONLY the raw A2UI JSON array — no prose, and never wrap it in "
        "<a2a_datapart_json> tags or 'kind'/'data'/'metadata' objects. "
        "\n\n### MEMORY & USER PREFERENCES:\n"
        "- You remember stated user preferences, personal facts, and health information across sessions using Vertex AI Memory Bank.\n"
        "- **CRITICAL**: Pay special attention to and explicitly remember all user allergies (e.g. food allergies, medication allergies, environmental allergies), dietary restrictions, and health requirements whenever the user mentions them.\n"
        "- Always check and respect retrieved user allergies and preferences in all subsequent conversations and recommendations."
    ),
    include_schema=True,
    include_examples=True,
)

root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model="gemini-flash-latest",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=instruction,
    code_executor=code_executor,
    tools=[
        PreloadMemoryTool(),
        list_tables,
        get_table_details,
        add_table,
        validate_and_explain_sql,
        fetch_data_tool_metadata,
        generate_diagram_image,
        generate_domain_video,
        get_weather,
        get_current_time,
    ],
    after_model_callback=a2ui_callback,
    after_agent_callback=generate_memories_callback,
)

app = App(
    root_agent=root_agent,
    name="app",
)
