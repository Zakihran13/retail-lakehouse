from __future__ import annotations

from datetime import datetime
from typing import Any


def norm(value: object) -> str:
    return " ".join(str(value).strip().lower().split())


def text(value: object) -> str | None:
    if value is None:
        return None
    if isinstance(value, float) and value.is_integer():
        return str(int(value))  # Excel gives 13085.0 for customer 13085
    return str(value).strip() or None


def required(row: dict[str, Any], key: str, where: str) -> Any:
    if row.get(key) is None:
        raise ValueError(f"{where}: missing required field {key!r}")
    return row[key]


def local_ts(value: object, where: str) -> datetime:
    if isinstance(value, datetime):
        return value.replace(tzinfo=None)  # keep wall time; UTC happens in dbt
    raise ValueError(f"{where}: expected a date, got {type(value).__name__}={value!r}")
