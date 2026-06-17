from unittest.mock import MagicMock, patch

import form.backup as backup_mod

# Test the data backup works and saves into csv
def test_backup_data_calls_two_endpoints_and_writes_csvs(tmp_path, monkeypatch):
    fake_file = str(tmp_path / "dummy" / "backup.py")
    # Create expected backups folder structure
    (tmp_path / "dummy" / ".." / "data" / "backups").mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(backup_mod, "__file__", fake_file)

    students_res = MagicMock(status_code=200, json=lambda: [{"student_id": "S1"}])
    class_res = MagicMock(status_code=200, json=lambda: [{"student_id": "S1", "classification": "A"}])

    with patch.object(backup_mod, "SUPABASE_URL", "https://example.supabase.co"), patch.object(
        backup_mod, "SUPABASE_KEY", "service-key"
    ), patch.object(backup_mod.requests, "get", side_effect=[students_res, class_res]) as mock_get, patch.object(
        backup_mod.pd.DataFrame, "to_csv"
    ) as mock_to_csv:

        backup_mod.backup_data()

        assert mock_get.call_count == 2
        students_endpoint = "https://example.supabase.co/rest/v1/STUDENT_DATA"
        class_endpoint = "https://example.supabase.co/rest/v1/CLASSIFICATION"

        assert mock_get.call_args_list[0][0][0] == students_endpoint
        assert mock_get.call_args_list[1][0][0] == class_endpoint

        assert mock_to_csv.call_count == 2


def test_backup_data_does_not_write_csv_on_non_200():
    students_res = MagicMock(status_code=500, text="oops", json=lambda: [])
    class_res = MagicMock(status_code=200, json=lambda: [{"student_id": "S1"}])

    with patch.object(backup_mod, "SUPABASE_URL", "https://example.supabase.co"), patch.object(
        backup_mod, "SUPABASE_KEY", "service-key"
    ), patch.object(backup_mod.requests, "get", side_effect=[students_res, class_res]), patch.object(
        backup_mod.pd.DataFrame, "to_csv"
    ) as mock_to_csv:

        backup_mod.backup_data()
        assert mock_to_csv.call_count == 1

