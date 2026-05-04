import pandas as pd
import os
from datetime import datetime, timezone

def load_data():
    csv_path = "data/STUDENTS - Sheet1.csv"
    if os.path.exists(csv_path):
        return pd.read_csv(csv_path)
    return pd.DataFrame()

def add_student_entry(**kwargs):
    CSV_PATH = "data/STUDENTS - Sheet1.csv"
    data_dict = kwargs.get('data_dict', {})
    
    # CRITICAL: Honor the student_id from API - NEVER OVERRIDE
    student_id = data_dict.get('student_id')
    
    data_dict.setdefault("created_at", datetime.now(timezone.utc).isoformat())
    
    # Load + append + save
    df_existing = pd.read_csv(CSV_PATH) if os.path.exists(CSV_PATH) else pd.DataFrame()
    new_row = pd.DataFrame([data_dict])
    df_new = pd.concat([df_existing, new_row], ignore_index=True)
    df_new.to_csv(CSV_PATH, index=False)
    
    print(f"SAVED Student ID {student_id}")
    return student_id

def process_data(df):
    numeric_cols = ['quant_score', 'logic_score', 'verbal_score', 'final_score', 'student_id']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    return df
