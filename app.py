import streamlit as st
import gspread
from google.oauth2 import service_account
import pandas as pd
import plotly.express as px
from datetime import datetime
import time
from frontend.bg import set_bg_image
from client import get_clients
from data.data import *
from frontend.styles import load_styles, set_page_config, auto_refresh
from filter import filter_data
from constants import SHEET_NAME, WORKSHEET_INDEX, REFRESH_SECONDS, USE_CSV, CSV_FILE

get_clients()

# Load all styles FIRST - this ensures they persist on refresh/rerun
load_styles()
set_bg_image()
set_page_config()

# USE_CSV and CSV_FILE now set in constants.py

col_refresh = st.columns([6, 1])
with col_refresh[1]:
    if st.button("🔄 Refresh"):
        st.rerun()

auto_refresh()

st.caption(f"Auto-refresh every {REFRESH_SECONDS} seconds | Last updated: {datetime.now().strftime('%H:%M:%S')}")

df = load_data()
df = process_data(df)

filter_data(df)
