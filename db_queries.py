from __future__ import annotations

from typing import Any

import pandas as pd

from constants import SUPA_DB, SUPA_RAW_DB
from supabase_client import get_supabase



def fetch_classification_df() -> pd.DataFrame:
    """Fetch rows from Supabase classification table into a DataFrame."""
    supa = get_supabase()

    res = supa.table(SUPA_DB).select("*").execute()
    rows: list[dict[str, Any]] = getattr(res, "data", None) or []
    return pd.DataFrame(rows)


def fetch_student_raw_df() -> pd.DataFrame:
    """Fetch rows from Supabase raw STUDENT_DATA table into a DataFrame."""
    supa = get_supabase()

    res = supa.table(SUPA_RAW_DB).select("*").execute()
    rows: list[dict[str, Any]] = getattr(res, "data", None) or []
    return pd.DataFrame(rows)



def append_student_entry(data_dict: dict[str, Any]) -> int | None:
    """Insert a row into Supabase classification table."""
    supa = get_supabase()

    payload = dict(data_dict)

    # If student_id is missing/blank, let DB generate it.
    if "student_id" in payload and payload["student_id"] in (None, ""):
        payload.pop("student_id")

    res = supa.table(SUPA_DB).insert(payload).execute()
    inserted: list[dict[str, Any]] = getattr(res, "data", None) or []

    if not inserted:
        return None

    return inserted[0].get("student_id")

