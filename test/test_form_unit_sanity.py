import pandas as pd

# Test sanity of the dataframe fixture used for filters in the form unit
def test_dataframe_fixture_shape_for_filters_is_ok():
    df = pd.DataFrame(
        [
            {"student_id": "S1", "college_name": "C1", "department": "D1", "year": 1, "final_score": 50},
            {"student_id": "S2", "college_name": "C2", "department": "D2", "year": 2, "final_score": 80},
        ]
    )
    assert set(df.columns) >= {"student_id", "college_name", "department", "year", "final_score"}
    assert df["final_score"].mean() == 65
