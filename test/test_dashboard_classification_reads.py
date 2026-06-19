from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from unittest.mock import patch
import os
import sys
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import queries.db_queries as dbq

@dataclass
class _FakeResponse:
    data: List[Dict[str, Any]]


class _FakeTable:
    def __init__(
        self,
        table_name: str,
        client: "_FakeSupabaseClient",
    ):
        self._table_name = table_name
        self._client = client
        self._select_called: Optional[str] = None
        self._insert_payload: Optional[Dict[str, Any]] = None

    def select(self, columns: str) -> "_FakeTable":
        self._select_called = columns
        return self

    def insert(self, payload: Dict[str, Any]) -> "_FakeTable":
        self._insert_payload = payload
        return self

    def execute(self) -> _FakeResponse:
        # Read path
        if self._insert_payload is None:
            self._client.select_calls.append((self._table_name, self._select_called))
            rows = self._client.read_data_by_table.get(self._table_name, [])
            return _FakeResponse(data=list(rows))

        self._client.insert_calls.append((self._table_name, dict(self._insert_payload)))
        return _FakeResponse(data=list(self._client.insert_result_rows))

class _FakeSupabaseClient:
    def __init__(
        self,
        read_data_by_table: Dict[str, List[Dict[str, Any]]],
        insert_result_rows: Optional[List[Dict[str, Any]]] = None,
    ):
        self.read_data_by_table = read_data_by_table
        self.insert_result_rows = insert_result_rows or []
        self.select_calls: List[Any] = []
        self.insert_calls: List[Any] = []

    def table(self, table: str) -> _FakeTable:
        return _FakeTable(table, client=self)

# Test cases for fetch_classification_df for read and marking
def test_fetch_classification_df_reads_classification_and_normalizes():
    fake_rows = [
        {
            "student_id": "C1",
            "college_name": "government college for women",
            "department": "bcom finance",
            "year": 3,
            "final_score": 88,
        },
        {
            "student_id": "C2",
            "college_name": "Christ College",
            "department": "computer applications",
            "year": 4,
            "final_score": 40,
        },
    ]

    fake_client = _FakeSupabaseClient(
        read_data_by_table={"CLASSIFICATION": fake_rows},
    )

    try:
        dbq.fetch_classification_df.clear()
    except Exception:
        pass

    with patch("queries.supabase_client.get_supabase", return_value=fake_client), patch.object(
        dbq, "get_supabase", return_value=fake_client
    ):
        df = dbq.fetch_classification_df()

    assert fake_client.select_calls == [("CLASSIFICATION", "*")]

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2

    assert df.loc[df["student_id"] == "C1", "college_name"].iloc[0] == "Government College For Women, Thiruvananthapuram"
    assert df.loc[df["student_id"] == "C1", "department"].iloc[0] == "BCom"

    assert df.loc[df["student_id"] == "C2", "college_name"].iloc[0] == "Christ College Vizhinjam"
    assert df.loc[df["student_id"] == "C2", "department"].iloc[0] == "BCA"

# Test that an empty CLASSIFICATION table returns an empty DataFrame
def test_fetch_classification_df_empty_table_returns_empty_df():
    fake_client = _FakeSupabaseClient(read_data_by_table={"CLASSIFICATION": []})

    try:
        dbq.fetch_classification_df.clear()
    except Exception:
        pass

    with patch("queries.supabase_client.get_supabase", return_value=fake_client), patch.object(
        dbq, "get_supabase", return_value=fake_client
    ):
        df = dbq.fetch_classification_df()

    assert isinstance(df, pd.DataFrame)
    assert df.empty
    assert fake_client.select_calls == [("CLASSIFICATION", "*")]

