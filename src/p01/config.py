from datetime import datetime, timedelta
import os

p01_url_source = os.getenv("P01_SOURCE_URL", "")
p01_duckdb_path = os.getenv("P01_DUCKDB_PATH", "")
p01_source_sha = os.getenv("P01_SOURCE_SHA256", "")
p01_workbook_sha = os.getenv("P01_WORKBOOK_SHA256", "")
p01_as_of_date = os.getenv("P01_AS_OF_DATE", "")
p01_max_late_ration = os.getenv("P01_MAX_LATE_RATIO", "")
p01_dagster_home = os.getenv("P01_DAGSTER_HOME", "")
p01_duckdb_threads = os.getenv("P01_DUCKDB_THREADS", "")
p01_log_level = os.getenv("P01_LOG_LEVEL", "")


# source header -> typed column; keys are normalised (lowercase, single-spaced)
COLUMNS = {
    "invoice": "invoice_no",
    "invoiceno": "invoice_no",
    "invoice no": "invoice_no",
    "stockcode": "stock_code",
    "stock code": "stock_code",
    "invoicedate": "invoice_ts_local",
    "invoice date": "invoice_ts_local",
    "quantity": "quantity",
    "price": "unit_price",
    "unitprice": "unit_price",
    "unit price": "unit_price",
    "customerid": "customer_id",
    "customer id": "customer_id",
    "country": "country",
}
