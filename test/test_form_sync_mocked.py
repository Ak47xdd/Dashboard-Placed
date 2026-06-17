import os
from unittest.mock import MagicMock, patch

import pandas as pd

import form.sync as sync_mod

# Test if the sync fuction for STUDENT_DATA works
def test_sync_STUDENT_csv_to_supabase_posts_to_correct_endpoint_and_headers(tmp_path):
    sample_df = pd.DataFrame({
        "student_id": ["S1", "S2"],
        "college_name": ["A", "B"],
        "department": ["X", "Y"],
    })

    with patch.object(sync_mod, "SUPABASE_URL", "https://example.supabase.co"), patch.object(
        sync_mod, "SUPABASE_KEY", "service-key"
    ), patch.object(sync_mod.pd, "read_csv", return_value=sample_df) as mock_read_csv, patch.object(
        sync_mod.requests, "post"
    ) as mock_post:

        mock_post.return_value = MagicMock(status_code=201, text="")

        # Act
        sync_mod.sync_STUDENT_csv_to_supabase()

        mock_read_csv.assert_called_once()

        expected_endpoint = "https://example.supabase.co/rest/v1/STUDENT_DATA"
        assert mock_post.call_count == 1
        called_endpoint = mock_post.call_args[0][0]
        assert called_endpoint == expected_endpoint

        called_headers = mock_post.call_args[1]["headers"]
        assert called_headers["apikey"] == "service-key"
        assert called_headers["Authorization"] == "Bearer service-key"
        assert called_headers["Content-Type"] == "application/json"
        assert called_headers["Prefer"] == "resolution=merge-duplicates"

        payload = mock_post.call_args[1]["json"]
        assert isinstance(payload, list)
        assert payload == sample_df.to_dict(orient="records")

# Test if the sync fuction for CLASSIFICATION works
def test_sync_CLASS_csv_to_supabase_handles_non_200_201_status():
    sample_df = pd.DataFrame({"student_id": ["S1"], "program": ["P1"]})

    with patch.object(sync_mod, "SUPABASE_URL", "https://example.supabase.co"), patch.object(
        sync_mod, "SUPABASE_KEY", "service-key"
    ), patch.object(sync_mod.pd, "read_csv", return_value=sample_df), patch.object(
        sync_mod.requests, "post"
    ) as mock_post:
        mock_post.return_value = MagicMock(status_code=400, text="bad")

        sync_mod.sync_CLASS_csv_to_supabase()

        expected_endpoint = "https://example.supabase.co/rest/v1/CLASSIFICATION"
        assert mock_post.call_args[0][0] == expected_endpoint

