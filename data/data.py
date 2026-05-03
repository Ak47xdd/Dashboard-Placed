import streamlit as st
import gspread
import pandas as pd
from google.oauth2 import service_account
from client import get_clients
from constants import USE_CSV, REFRESH_SECONDS, CSV_FILE, SHEET_NAME, WORKSHEET_INDEX

@st.cache_data(ttl=REFRESH_SECONDS)
def load_data():
    if USE_CSV:
        # Load from local CSV file for testing
        df = pd.read_csv(f"data/{CSV_FILE}")
    else:
        # Load from Google Sheets
        client = get_clients()
        sheet = client.open(SHEET_NAME).get_worksheet(WORKSHEET_INDEX)
        records = sheet.get_all_records()
        df = pd.DataFrame(records)
    return df

def process_data(df):
    """Process and clean the new classifications dataframe"""
    # Set student_id as unique index
    df['student_id'] = df['student_id'].astype(int)
    df = df.set_index('student_id')
    
    # Convert all scores to numeric
    score_columns = ['quant_score', 'logic_score', 'verbal_score', 'final_score']
    for col in score_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    return df

