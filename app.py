"""
Main Streamlit app entry point. Responsible for loading styles, data, 
and rendering the appropriate dashboard based on user selection.
"""

import streamlit as st
from datetime import datetime
from frontend.bg import set_bg_image
from data.data import load_data, process_data
from frontend.styles import load_styles, set_page_config, auto_refresh
from filter import filter_data
from constants import REFRESH_SECONDS
 
load_styles()
set_bg_image()
set_page_config()
 
col_refresh = st.columns([6, 1])
with col_refresh[1]:
    if st.button("🔄 Refresh"):
        st.cache_data.clear()
        for _key in ["df_raw", "df_classification"]:
            st.session_state.pop(_key, None)
        st.rerun()
 
auto_refresh()
 
st.caption(f"Auto-refresh every {REFRESH_SECONDS} seconds | Last updated: {datetime.now().strftime('%H:%M:%S')}")
 
data_view = st.sidebar.radio(
    "📌 Data view",
    options=["Response Dashboard", "Student Evaluation Dashboard"],
    index=0,
    help="Choose 'Response Dashboard' to explore aggregated insights from student responses. Choose 'Student Evaluation Dashboard' to view detailed student-level data and filter by various criteria.",
)
 
view = "raw" if data_view.startswith("Student") else "classification"
 
cache_key = f"df_{view}"
if cache_key not in st.session_state:
    df = load_data(view=view)
    if view == "classification":
        df = process_data(df)
    st.session_state[cache_key] = df
 
filter_data(st.session_state[cache_key], view=view)