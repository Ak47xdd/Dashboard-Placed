import streamlit as st
import gspread
from google.oauth2 import service_account

@st.cache_resource
def get_clients():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = service_account.Credentials.from_service_account_file(
        "service_key.json", scopes=scopes
    )
    return gspread.authorize(creds)