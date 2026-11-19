"""Land every source row in raw.invoice_lines.

Scope: read rows, record where each came from, write once.
No dedupe, no timezone maths, no business keys - those are dbt's job.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import uuid
from collections.abc import Iterator
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any
from loguru import logger

import duckdb
from openpyxl import load_workbook
from p01.config import COLUMNS
from p01.ingest.data.db_loader import load_schema
from p01.ingest.data.statement import INSERT
from p01.utils.helper import norm, text, required, local_ts


def iter_source_rows(path: Path) -> Iterator[tuple[str, int, dict[str, Any]]]:
    logger.info(f"Reading File {path}")
    workbook = load_workbook(path, read_only=True, data_only=True)
    try:
        for sheet in workbook.worksheets:
            logger.info(f"Iterating Worksheet: {sheet.title}")
            columns: dict[int, str] = {}  # index -> canonical name
            originals: dict[int, str] = {}  # index -> source header text
            
            for row_no, row in enumerate(sheet.iter_rows(values_only=True), start=1):
                if not columns:
                    for index, cell in enumerate(row):
                        name = COLUMNS.get(norm(cell)) if cell is not None else None
                        if name is not None:
                            columns[index] = name
                            originals[index] = str(cell).strip()
                    if "invoice_no" not in columns.values():
                        columns.clear()
                        originals.clear()  # title row above the real header
                    continue
                if all(cell is None for cell in row):
                    continue
                yield sheet.title, row_no, {
                    columns[i]: row[i] if i < len(row) else None for i in columns
                }
    finally:
        workbook.close()


def _record(
    sheet: str,
    row_no: int,
    row: dict[str, Any],
    workbook_hash: str,
    ingested_at: datetime,
) -> tuple[Any, ...]:
    where = f"{sheet}!{row_no}"
    return (
        str(uuid.uuid4()),
        workbook_hash,
        sheet,
        row_no,
        ingested_at,
        text(required(row, "invoice_no", where)),
        text(required(row, "stock_code", where)),
        local_ts(required(row, "invoice_ts_local", where), where),
        int(required(row, "quantity", where)),
        Decimal(str(required(row, "unit_price", where))),
        text(row.get("customer_id")),
        text(row.get("country")),
        json.dumps(row, default=str),
    )


def _count(con: duckdb.DuckDBPyConnection) -> int:
    result = con.execute("select count(*) from raw.invoice_lines").fetchone()
    assert result is not None
    return int(result[0])


def load(source: Path, db_path: Path, batch_size: int = 5_000) -> tuple[int, int]:
    logger.info(f"Checking Database at: {db_path}")
    db_path.parent.mkdir(parents=True, exist_ok=True)

    workbook_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    ingested_at = datetime.now(timezone.utc)

    logger.info(f"Connecting db at: {db_path}")
    con = duckdb.connect(str(db_path))
    try:
        logger.info("Checking schema and total data!")
        load_schema(con)
        before = _count(con)

        n_stop = 0
        batch: list[tuple[Any, ...]] = []
        for sheet, row_no, row in iter_source_rows(source):
            batch.append(_record(sheet, row_no, row, workbook_hash, ingested_at))
            if len(batch) >= batch_size:
                con.executemany(INSERT, batch)
                batch.clear()

                n_stop += 1
                if n_stop >= 2:
                    break

            

        if batch:
            con.executemany(INSERT, batch)

        return _count(con) - before, _count(con)
    except Exception as e:
        logger.error(f"found error at {sheet}: {e}")
    finally:
        con.close()


def main() -> int:
    parser = argparse.ArgumentParser(prog="p01.ingest.load_raw")
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument(
        "--db",
        type=Path,
        default=Path(os.environ.get("P01_DUCKDB_PATH", "data/retail.duckdb")),
    )
    args = parser.parse_args()

    logger.info("Starting Process!")
    inserted, total = load(args.source, args.db)
    print(f"inserted {inserted}, total {total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
