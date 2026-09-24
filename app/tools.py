import json
from typing import List, Optional
import urllib.request
from google.cloud import firestore
import sqlparse

FIRESTORE_PROJECT = "qwiklabs-gcp-02-502ecf129e21"


def get_firestore_db() -> firestore.Client:
    """Returns a Firestore client initialized with the hardcoded project ID."""
    return firestore.Client(project=FIRESTORE_PROJECT)


def list_tables(schema_name: Optional[str] = None) -> str:
    """Lists database tables stored in the Firestore data catalog.

    Args:
        schema_name: Optional schema filter (e.g. 'public', 'analytics', 'inventory').

    Returns:
        A formatted string summary of tables found in the catalog.
    """
    try:
        db = get_firestore_db()
        collection_ref = db.collection("tables")

        if schema_name:
            docs = collection_ref.where("schema_name", "==", schema_name).stream()
        else:
            docs = collection_ref.stream()

        tables = []
        for doc in docs:
            data = doc.to_dict()
            tables.append(
                f"- Table: {data.get('table_name')} (Schema: {data.get('schema_name')}, Dialect: {data.get('dialect')}, Rows: {data.get('row_count'):,})\n"
                f"  Description: {data.get('description')}"
            )

        if not tables:
            return f"No tables found in catalog matching schema '{schema_name}'." if schema_name else "No tables found in catalog."

        return "Database Tables Catalog:\n" + "\n".join(tables)
    except Exception as e:
        return f"Error listing tables from Firestore: {e}"


def get_table_details(table_name: str) -> str:
    """Retrieves full details for a specific table including column definitions from Firestore.

    Args:
        table_name: The name of the table to look up (e.g. 'users', 'orders_fact', 'product_catalog').

    Returns:
        Formatted string details of the table and its schema columns.
    """
    try:
        db = get_firestore_db()
        docs = db.collection("tables").where("table_name", "==", table_name.lower().strip()).limit(1).stream()

        doc_list = list(docs)
        if not doc_list:
            return f"Table '{table_name}' was not found in the Firestore catalog."

        data = doc_list[0].to_dict()
        columns_str = "\n".join([f"  • {col}" for col in data.get("columns", [])])

        return (
            f"Table Details: {data.get('schema_name')}.{data.get('table_name')}\n"
            f"Dialect: {data.get('dialect')}\n"
            f"Estimated Row Count: {data.get('row_count'):,}\n"
            f"Description: {data.get('description')}\n"
            f"Columns:\n{columns_str}"
        )
    except Exception as e:
        return f"Error fetching table details for '{table_name}': {e}"


def add_table(
    table_name: str,
    schema_name: str,
    dialect: str,
    row_count: int,
    description: str,
    columns: List[str],
) -> str:
    """Adds a new database table or updates an existing table definition in the Firestore catalog.

    Args:
        table_name: Name of the table (e.g. 'clickstream_events').
        schema_name: Schema containing the table (e.g. 'public', 'analytics').
        dialect: Database dialect (e.g. 'PostgreSQL', 'BigQuery', 'Snowflake').
        row_count: Estimated total number of rows.
        description: Functional overview of what data this table stores.
        columns: List of column definitions with types (e.g. ['event_id UUID PRIMARY KEY', 'user_id INT', 'event_type VARCHAR']).

    Returns:
        A confirmation message indicating successful store/update in Firestore.
    """
    try:
        db = get_firestore_db()
        doc_id = f"{schema_name}_{table_name}".lower().replace(".", "_")

        doc_data = {
            "table_name": table_name.lower().strip(),
            "schema_name": schema_name.lower().strip(),
            "dialect": dialect,
            "row_count": row_count,
            "description": description,
            "columns": columns,
        }

        db.collection("tables").document(doc_id).set(doc_data)
        return f"Successfully saved table '{schema_name}.{table_name}' to Firestore catalog (Document ID: '{doc_id}')."
    except Exception as e:
        return f"Error adding table '{table_name}' to Firestore: {e}"


def validate_and_explain_sql(sql_query: str, dialect: str = "PostgreSQL") -> str:
    """Validates, formats, and analyzes a SQL query for potential performance anti-patterns.

    Args:
        sql_query: The raw SQL query string to format and analyze.
        dialect: The target SQL dialect (e.g. 'PostgreSQL', 'BigQuery', 'Snowflake').

    Returns:
        A formatted summary including statement type, cleaned SQL code, and optimization recommendations.
    """
    try:
        formatted_sql = sqlparse.format(sql_query, reindent=True, keyword_case="upper")
        parsed = sqlparse.parse(sql_query)

        recommendations = []
        lower_query = sql_query.lower()

        if "select *" in lower_query:
            recommendations.append("Avoid 'SELECT *': Explicitly name columns to reduce I/O and network payload.")
        if "where" not in lower_query and ("select" in lower_query or "delete" in lower_query or "update" in lower_query):
            recommendations.append("Missing WHERE clause: Query performs a full table scan. Add indexing or partition filters.")
        if "order by" in lower_query and "limit" not in lower_query:
            recommendations.append("ORDER BY without LIMIT: Sorting un-capped datasets can cause high memory usage.")

        statement_type = parsed[0].get_type() if parsed else "UNKNOWN"

        recs_str = "\n".join([f"  • {rec}" for rec in recommendations]) if recommendations else "  • Query follows basic SQL performance best practices."

        return (
            f"SQL Analysis ({dialect}):\n"
            f"Statement Type: {statement_type}\n\n"
            f"Formatted SQL:\n```sql\n{formatted_sql}\n```\n\n"
            f"Optimization Advice:\n{recs_str}"
        )
    except Exception as e:
        return f"Error analyzing SQL query: {e}"


def fetch_data_tool_metadata(repo_path: str = "duckdb/duckdb") -> str:
    """Fetches real-time repository metadata, star counts, open issues, and primary language for open-source data engineering tools and database engines.

    Args:
        repo_path: GitHub repository in 'owner/repo' format (e.g. 'duckdb/duckdb', 'apache/spark', 'dbt-labs/dbt-core', 'postgres/postgres').

    Returns:
        Formatted string with live GitHub repository metrics.
    """
    try:
        clean_repo = repo_path.strip().lower()
        if clean_repo.startswith("https://github.com/"):
            clean_repo = clean_repo.replace("https://github.com/", "")

        url = f"https://api.github.com/repos/{clean_repo}"
        req = urllib.request.Request(url, headers={"User-Agent": "DataCraft-Agent/1.0"})

        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())

        return (
            f"Data Tool Repository: {data.get('full_name')}\n"
            f"Description: {data.get('description', 'N/A')}\n"
            f"Primary Language: {data.get('language', 'N/A')}\n"
            f"GitHub Stars: {data.get('stargazers_count', 0):,}\n"
            f"Forks: {data.get('forks_count', 0):,}\n"
            f"Open Issues: {data.get('open_issues_count', 0):,}\n"
            f"License: {data.get('license', {}).get('name', 'N/A') if data.get('license') else 'N/A'}\n"
            f"Repository URL: {data.get('html_url')}"
        )
    except Exception as e:
        return f"Error fetching GitHub repository metadata for '{repo_path}': {e}"
