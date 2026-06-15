"""
Backup both tables "STUDENT_DATA" and "CLASSIFICATION" from Supabase. 
This is a utility endpoint to fetch all data from both tables and return as JSON or CSV. 
Not exposed publicly.
"""

import os
import requests
import pandas as pd
from dotenv import load_dotenv
load_dotenv()

MAIN_TABLE_NAME = "STUDENT_DATA"
CLASS_TABLE_NAME = "CLASSIFICATION"
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def backup_data():
    """
    Fetch all data from both tables and return as JSON or CSV.
    """
    
    curr = os.path.dirname(__file__)
    data_dir = os.path.abspath(os.path.join(curr, "..", "data/backups"))
    
    RAW_CSV_PATH = os.path.join(data_dir, "STUDENT_DATA.csv")
    CLASS_CSV_PATH = os.path.join(data_dir, "CLASSIFICATION.csv")
    
    STUDENTS_ENDPOINT = f"{SUPABASE_URL}/rest/v1/{MAIN_TABLE_NAME}"
    CLASSIFICATION_ENDPOINT = f"{SUPABASE_URL}/rest/v1/{CLASS_TABLE_NAME}"
    
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
    }
    
    query = {
    "select": "*",
    "order": "student_id.asc" 
    }
    
    students_res = requests.get(STUDENTS_ENDPOINT, headers=headers, params=query)
    classification_res = requests.get(CLASSIFICATION_ENDPOINT, headers=headers, params=query)
    
    if students_res.status_code == 200:
        students_data = students_res.json()
        pd.DataFrame(students_data).to_csv(RAW_CSV_PATH, index=False, mode='w')
        print(f"Backed up STUDENT_DATA to {RAW_CSV_PATH}")
    else :
        print(f"Failed to backup STUDENT_DATA: {students_res.status_code} - {students_res.text}")
    
    if classification_res.status_code == 200:
        classification_data = classification_res.json()
        pd.DataFrame(classification_data).to_csv(CLASS_CSV_PATH, index=False, mode='w')
        print(f"Backed up CLASSIFICATION to {CLASS_CSV_PATH}")
    else:
        print(f"Failed to backup CLASSIFICATION: {classification_res.status_code} - {classification_res.text}")

if __name__ == "__main__":
    backup_data()