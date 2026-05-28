"""
This module is responsible for syncing the local CSV files to the Supabase database.
Use this to add bulk data from the csv located in the data/ folder to the Supabase tables. 
This is a one-time utility to populate the database with existing data.
"""

import pandas as pd
import requests
import os
from dotenv import load_dotenv  
load_dotenv()

MAIN_TABLE_NAME = "STUDENT_DATA"
CLASS_TABLE_NAME = "CLASSIFICATION"
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def sync_STUDENT_csv_to_supabase():
    df = pd.read_csv('./data/STUDENTS - Sheet1.csv')
    print("Synced STUDENT_DATA CSV to Supabase table")

    records = df.to_dict(orient='records')

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates"
    }
    
    endpoint = f"{SUPABASE_URL}/rest/v1/{MAIN_TABLE_NAME}"
    res = requests.post(endpoint, headers=headers, json=records)

    if res.status_code in [200, 201]:
        print("Successfully synced STUDENT data!")
    else:
        print(f"Error: {res.status_code} - {res.text}")
        
def sync_CLASS_csv_to_supabase():
    df = pd.read_csv('./data/CLASSIFICATIONS - Sheet1 (1).csv')
    print("Synced CLASSIFICATION CSV to Supabase table")

    records = df.to_dict(orient='records')

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates"
    }
    
    endpoint = f"{SUPABASE_URL}/rest/v1/{CLASS_TABLE_NAME}"
    res = requests.post(endpoint, headers=headers, json=records)

    if res.status_code in [200, 201]:
        print("Successfully synced CLASSIFICATION data!")
    else:
        print(f"Error: {res.status_code} - {res.text}")