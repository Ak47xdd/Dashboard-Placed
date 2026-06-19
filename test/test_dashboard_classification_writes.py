from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from unittest.mock import patch
import os
import sys

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
        if self._insert_payload is None:
            self._client.select_calls.append((self._table_name, self._select_called))
            rows = self._client.read_data_by_table.get(self._table_name, [])
            return _FakeResponse(data=list(rows))

        self._client.insert_calls.append((self._table_name, dict(self._insert_payload)))
        return _FakeResponse(data=list(self._client.insert_result_rows))

class _FakeSupabaseClient:
    def __init__(
        self,
        read_data_by_table: Optional[Dict[str, List[Dict[str, Any]]]] = None,
        insert_result_rows: Optional[List[Dict[str, Any]]] = None,
    ):
        self.read_data_by_table = read_data_by_table or {}
        self.insert_result_rows = insert_result_rows or []
        self.select_calls: List[Any] = []
        self.insert_calls: List[Any] = []

    def table(self, table: str) -> _FakeTable:
        return _FakeTable(table, client=self)

# Test student entry to CLASSIFICATION table
def test_append_student_entry_omits_blank_student_id_and_inserts_into_classification():
    fake_client = _FakeSupabaseClient(
        insert_result_rows=[{"student_id": "DB_GENERATED_ID"}],
    )

    payload = {
        "student_id": "",
        "college_name": "Christ College Vizhinjam",
        "department": "BCA",
        "year": 1,
        "final_score": 90,
    }

    with patch(
        "queries.supabase_client.get_supabase",
        return_value=fake_client,
    ), patch.object(dbq, "get_supabase", return_value=fake_client):
        inserted_id = dbq.append_student_entry(payload)

    assert inserted_id == "DB_GENERATED_ID"
    assert len(fake_client.insert_calls) == 1

    table_name, sent_payload = fake_client.insert_calls[0]
    assert table_name == "CLASSIFICATION"

    assert "student_id" not in sent_payload
    assert sent_payload["college_name"] == "Christ College Vizhinjam"
    assert sent_payload["department"] == "BCA"

# Test student entry with None student_id to CLASSIFICATION table
def test_append_student_entry_omits_none_student_id():
    fake_client = _FakeSupabaseClient(insert_result_rows=[{"student_id": "X1"}])

    payload = {
        "student_id": None,
        "college_name": "Amrita Vishwa Vidyapeetham Mysore",
        "department": "BCA + MCA",
        "year": 2,
    }

    with patch(
        "queries.supabase_client.get_supabase",
        return_value=fake_client,
    ), patch.object(dbq, "get_supabase", return_value=fake_client):
        inserted_id = dbq.append_student_entry(payload)

    assert inserted_id == "X1"
    assert fake_client.insert_calls[0][0] == "CLASSIFICATION"

    sent_payload = fake_client.insert_calls[0][1]
    assert "student_id" not in sent_payload
    assert sent_payload["college_name"] == "Amrita Vishwa Vidyapeetham Mysore"

