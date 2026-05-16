from __future__ import annotations
from typing import Any
import pandas as pd
import streamlit as st
 
from constants import SUPA_DB, SUPA_RAW_DB
from supabase_client import get_supabase
 
 
def _normalize(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize college_name and department spelling variants using canonical maps.
    Called once at fetch time so the result is cached with the data — never runs
    again until the cache expires.
    """
    from college_dept_map import COLLEGE_VARIANT_CANONICAL_MAP, DEPARTMENT_VARIANT_CANONICAL_MAP
 
    out = df.copy()
 
    if "college_name" in out.columns and COLLEGE_VARIANT_CANONICAL_MAP:
        s = out["college_name"].fillna("").astype(str).str.strip()
        cn_map = {k.lower(): v for k, v in COLLEGE_VARIANT_CANONICAL_MAP.items()}
        s_lower = s.str.lower()
        for wrong, canonical in cn_map.items():
            s.loc[s_lower.eq(wrong)] = canonical
        out["college_name"] = s
 
    if "department" in out.columns and DEPARTMENT_VARIANT_CANONICAL_MAP:
        s = out["department"].fillna("").astype(str).str.strip()
        dn_map = {k.lower(): v for k, v in DEPARTMENT_VARIANT_CANONICAL_MAP.items()}
        s_lower = s.str.lower()
        for wrong, canonical in dn_map.items():
            s.loc[s_lower.eq(wrong)] = canonical
        out["department"] = s
 
    return out
 
 
@st.cache_data(ttl=30)
def fetch_classification_df() -> pd.DataFrame:
    """Fetch rows from Supabase classification table into a DataFrame."""
    supa = get_supabase()
    res = supa.table(SUPA_DB).select("*").execute()
    rows: list[dict[str, Any]] = getattr(res, "data", None) or []
    df = pd.DataFrame(rows)
    return _normalize(df)
 
 
@st.cache_data(ttl=30)
def fetch_student_raw_df() -> pd.DataFrame:
    """
    Fetch rows from Supabase raw STUDENT_DATA table into a DataFrame.
    Normalization is applied here so it only runs once per cache cycle.
    """
    supa = get_supabase()
    res = supa.table(SUPA_RAW_DB).select("*").execute()
    rows: list[dict[str, Any]] = getattr(res, "data", None) or []
    df = pd.DataFrame(rows)
    return _normalize(df)
 
 
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
 