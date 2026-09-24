# DataCraft — Data Engineering & SQL Assistant

**DataCraft** is an autonomous AI agent built on the Google Agent Development Kit (ADK) that assists data engineers with database schema management, query optimization, data tool research, architecture visualization, and domain video generation.

---

## 🛠️ Key Capabilities & Features

Based on the implemented tools in [`app/tools.py`](app/tools.py) and [`app/agent.py`](app/agent.py):

* **Database Schema Catalog (Firestore)**:
  * **List Tables (`list_tables`)**: Queries the Firestore catalog to display registered database tables, row counts, and dialect details.
  * **Table Details (`get_table_details`)**: Fetches column definitions, data types, and primary keys for specific tables.
  * **Add Table (`add_table`)**: Registers or updates database table definitions in the Firestore schema catalog.

* **SQL Analysis & Optimization (`validate_and_explain_sql`)**:
  * Formats raw SQL queries using `sqlparse`.
  * Detects performance anti-patterns (e.g., `SELECT *` full table scans, missing `WHERE` clauses, un-capped `ORDER BY` statements).
  * Provides dialect-specific optimization recommendations (PostgreSQL, BigQuery, Snowflake).

* **Open-Source Data Engineering Tool Metadata (`fetch_data_tool_metadata`)**:
  * Queries GitHub REST APIs to fetch real-time star counts, open issue metrics, primary languages, and license information for tools like DuckDB, Apache Spark, and dbt.

* **Architecture Diagram Generation (`generate_diagram_image`)**:
  * Uses `gemini-3.1-flash-lite-image` to generate visual ER diagrams and data pipeline architecture diagrams.
  * Uploads generated images to Google Cloud Storage.

* **Domain Video Visualization (`generate_domain_video`)**:
  * Uses Google's `gemini-omni-flash-preview` model in the `global` region via the Vertex AI Interactions API to generate animated video visualizations for data streaming and ETL concepts.
  * Saves artifacts in the Playground panel via `tool_context.save_artifact` and uploads video bytes straight from memory to Google Cloud Storage.

* **Code Execution Sandbox (`AgentEngineSandboxCodeExecutor`)**:
  * Runs Python scripts in a secure Vertex AI Agent Engine sandbox to compute statistics and schema diffs.

---

## ☁️ Integrated Google Cloud Services

* **Vertex AI Memory Bank**: Persists user database preferences, target dialects, and history across conversation sessions (`PreloadMemoryTool` + `generate_memories_callback`).
* **Google Cloud Firestore**: Serves as the database table catalog (`tables` collection).
* **Google Cloud Storage (GCS)**: Stores generated architecture diagrams and video assets.
* **Vertex AI Reasoning Engine / Agent Runtime**: Hosts the deployed agent backend.
* **A2UI (v0.8)**: Generates structured, responsive A2UI cards for table listings, SQL analysis summaries, and media previews.

---

## 🎬 Generated Media & Demo Assets

* **Domain Video (`gemini-omni-flash-preview`)**: [Kafka to BigQuery Event Streaming Video](https://storage.googleapis.com/datacraft-assets-qwiklabs-gcp-02-502ecf129e21/video_49e8f4d6.mp4)
* **Upbeat Lo-Fi Soundtrack**: [datacraft_demo_lofi_music.wav](https://storage.googleapis.com/datacraft-assets-qwiklabs-gcp-02-502ecf129e21/datacraft_demo_lofi_music.wav)
* **Architecture Diagram**: [PostgreSQL to BigQuery Pipeline Diagram](https://storage.googleapis.com/datacraft-assets-qwiklabs-gcp-02-502ecf129e21/diagram_7f7b4389.jpg)

---

## 📁 Repository Structure

```
datacraft/
├── app/
│   ├── agent.py               # Main agent configuration, A2UI prompt, and root agent definition
│   ├── tools.py               # Custom tools (Firestore catalog, SQL optimizer, diagram & video gen)
│   ├── a2ui_utils.py          # A2UI callback transformer for ADK web and A2A clients
│   └── __init__.py
├── frontend/
│   ├── main.py                # FastAPI proxy connecting browser to deployed agent over A2A protocol
│   └── static/
│       └── index.html         # Custom chat frontend with dark slate/indigo theme & A2UI renderer
├── tests/                     # Unit and integration tests
├── agents-cli-manifest.yaml   # Agent manifest configuration
├── deployment_metadata.json   # Deployment target metadata
├── pyproject.toml             # Project dependencies
└── README.md                  # Project documentation
```

---

## 🚀 Local Development & Setup

### Prerequisites

Ensure you have the following installed:
* **Python 3.10+**
* **uv**: Python package and project manager (`pip install uv`)
* **agents-cli**: Install via `uv tool install google-agents-cli`
* **Google Cloud SDK**: Authenticated with `gcloud auth application-default login`

### Installation

1. Install project dependencies:
   ```bash
   agents-cli install
   ```

2. (Optional) Seed the local Firestore data catalog:
   ```bash
   uv run python seed_firestore.py
   ```

### Running Locally

* **Run the ADK Playground (Interactive Developer UI)**:
  ```bash
  agents-cli playground
  ```

* **Run the FastAPI Chat Frontend locally**:
  ```bash
  cd frontend
  pip install -r requirements.txt
  export AGENT_ENGINE_RESOURCE_NAME="<your-reasoning-engine-resource-name>"
  export AGENT_DIRECTORY="app"
  python main.py
  ```

---

## 🧪 Testing & Evaluation

* **Run Unit and Integration Tests**:
  ```bash
  uv run pytest tests/unit tests/integration
  ```

* **Evaluate Agent Performance**:
  ```bash
  agents-cli eval generate
  agents-cli eval grade
  ```

---

## 🚢 Deployment

To deploy the agent to Vertex AI Agent Runtime:

```bash
agents-cli deploy --project <your-gcp-project-id> --no-confirm-project
```
