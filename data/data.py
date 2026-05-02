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
        df = pd.read_csv(CSV_FILE)
    else:
        # Load from Google Sheets
        client = get_clients()
        sheet = client.open(SHEET_NAME).get_worksheet(WORKSHEET_INDEX)
        records = sheet.get_all_records()
        df = pd.DataFrame(records)
    return df

def process_data(df):
    """Process and clean the dataframe"""
    # Convert hours spent to numeric
    df['Hours spent'] = pd.to_numeric(df['Hours spent'], errors='coerce')
    
    # Parse date of enrollment
    df['Date of Enrollment'] = pd.to_datetime(df['Date of Enrollment'], format='%d/%m/%Y', errors='coerce')
    
    # Parse timestamp
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], format='%d/%m/%Y %H:%M:%S', errors='coerce')
    
    return df
