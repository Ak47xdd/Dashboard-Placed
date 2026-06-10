"""
Styling utilities for the Streamlit app. 
This module is responsible for loading external CSS, HTML templates, 
and JavaScript files to enhance the appearance and functionality of the dashboard. 
It also defines functions for setting page configuration and implementing auto-refresh with a countdown timer.
"""

import streamlit as st
import os
from constants import REFRESH_SECONDS

FRONTEND_DIR = os.path.dirname(os.path.abspath(__file__))

def load_styles():
    """
    Load all external styles, templates, and scripts - call this on every rerun
    """
    
    css_file_path = os.path.join(FRONTEND_DIR, "css/styles.css")
    try:
        with open(css_file_path, "r") as f:
            css_content = f.read()
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass
    
    title_file_path = os.path.join(FRONTEND_DIR, "title.html")
    try:
        with open(title_file_path, "r") as f:
            title_content = f.read()
        st.markdown(title_content, unsafe_allow_html=True)
    except FileNotFoundError:
        pass
    
    st.markdown(
        f'<script>var REFRESH_SECONDS = {REFRESH_SECONDS};</script>',
        unsafe_allow_html=True
    )

    script_file_path = os.path.join(FRONTEND_DIR, "script.js")
    try:
        with open(script_file_path, "r") as f:
            script_content = f.read()
        st.markdown(f"<script>{script_content}</script>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass

    filter_css_path = os.path.join(FRONTEND_DIR, "css/filter_styles.css")
    try:
        with open(filter_css_path, "r") as f:
            filter_css = f.read()
        st.markdown(f"<style>{filter_css}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass

def set_page_config():
    """Set Streamlit page configuration - call this once at app start"""
    st.set_page_config(
        page_title="Placed Dashboard",
        layout="wide",
        page_icon="📊",
        initial_sidebar_state="expanded"
    )

def auto_refresh():
    """Enhanced auto-refresh with improved styling"""
    countdown_file_path = os.path.join(FRONTEND_DIR, "countdown.html")
    try:
        with open(countdown_file_path, "r") as f:
            countdown_content = f.read()
        st.markdown(countdown_content, unsafe_allow_html=True)
    except FileNotFoundError:
        pass
