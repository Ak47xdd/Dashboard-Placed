import streamlit as st
from datetime import datetime
from frontend.bg import set_bg_image
from data.data import *
from frontend.styles import load_styles, set_page_config, auto_refresh
from filter import filter_data
from constants import REFRESH_SECONDS


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
