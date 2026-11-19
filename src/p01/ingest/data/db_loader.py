import duckdb
from p01.config import p01_duckdb_path


def load_schema(client, duckdb_path: str = p01_duckdb_path):
    # client = duckdb.connect(p01_duckdb_path)

    with open("src/p01/ingest/data/schema.sql", "r") as f:
        schema = f.read()

    return client.execute(schema)

