import sys
from google.cloud import firestore

FIRESTORE_PROJECT = "qwiklabs-gcp-02-502ecf129e21"

INITIAL_TABLES = [
    {
        "id": "users_table",
        "table_name": "users",
        "schema_name": "public",
        "dialect": "PostgreSQL",
        "row_count": 1250000,
        "description": "Core user account records including authentication metadata and profile preferences.",
        "columns": [
            "id BIGINT PRIMARY KEY",
            "email VARCHAR(255) UNIQUE",
            "created_at TIMESTAMP",
            "is_active BOOLEAN"
        ]
    },
    {
        "id": "orders_fact",
        "table_name": "orders_fact",
        "schema_name": "analytics",
        "dialect": "BigQuery",
        "row_count": 45000000,
        "description": "Fact table containing raw transactional order details, customer IDs, and financial metrics.",
        "columns": [
            "order_id STRING",
            "customer_id STRING",
            "amount NUMERIC",
            "order_timestamp TIMESTAMP",
            "status STRING"
        ]
    },
    {
        "id": "product_catalog",
        "table_name": "product_catalog",
        "schema_name": "inventory",
        "dialect": "Snowflake",
        "row_count": 85000,
        "description": "Dimension table mapping product SKUs, categories, pricing, and stock levels.",
        "columns": [
            "sku VARCHAR",
            "name VARCHAR",
            "category VARCHAR",
            "price NUMBER(10,2)",
            "stock_quantity INT"
        ]
    }
]

def seed_database():
    print(f"Connecting to Firestore with project ID: {FIRESTORE_PROJECT}...")
    db = firestore.Client(project=FIRESTORE_PROJECT)
    collection_ref = db.collection("tables")

    for item in INITIAL_TABLES:
        doc_id = item["id"]
        doc_data = {k: v for k, v in item.items() if k != "id"}
        collection_ref.document(doc_id).set(doc_data)
        print(f"Seeded table document '{doc_id}' into 'tables' collection.")

    print("Firestore database seeded successfully!")

if __name__ == "__main__":
    seed_database()
