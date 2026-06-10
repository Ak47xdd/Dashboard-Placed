"""
Data loading and processing utilities for the Student Evaluation Dashboard.
"""

import pandas as pd
import os
from datetime import datetime, timezone

from constants import USE_CSV
from queries.db_queries import fetch_classification_df, append_student_entry, fetch_student_raw_df

def load_data(view: str = "classification"):
    """
    Load either classified scores or raw student data.

    view:
      - "classification" => Supabase CLASSIFICATION table (scores)
      - "raw" => Supabase STUDENT_DATA table (questionnaire + metadata)
    """
    
    # load from local CSV files (refer constants.py for USE_CSV flag).
    if USE_CSV:
        if view == "raw":
            csv_path = "data/backups/STUDENT_DATA.csv"
        else:
            csv_path = "data/backups/CLASSIFICATION.csv"

        if os.path.exists(csv_path):
            return pd.read_csv(csv_path)
        return pd.DataFrame()

    if view == "raw":
        return fetch_student_raw_df()

    return fetch_classification_df()

def add_student_entry(**kwargs):
    """
    Insert into Supabase or append to local CSV depending on USE_CSV.
    """
    
    data_dict = kwargs.get('data_dict', {})

    student_id = data_dict.get('student_id')

    data_dict.setdefault("created_at", datetime.now(timezone.utc).isoformat())

    if USE_CSV:
        CSV_PATH = "STUDENT_DATA.csv"

        df_existing = pd.read_csv(CSV_PATH) if os.path.exists(CSV_PATH) else pd.DataFrame()
        new_row = pd.DataFrame([data_dict])
        df_new = pd.concat([df_existing, new_row], ignore_index=True)
        df_new.to_csv(CSV_PATH, index=False)

        print(f"SAVED Student ID {student_id}")
        return student_id

    inserted_id = append_student_entry(data_dict)
    return inserted_id if inserted_id is not None else student_id

def process_data(df):
    numeric_cols = ['quant_score', 'logic_score', 'verbal_score', 'final_score', 'student_id']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    return df
