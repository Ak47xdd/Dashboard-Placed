import streamlit as st
import os

def set_bg_image():
    """Set background image with enhanced overlay for better readability"""
    frontend_dir = os.path.dirname(os.path.abspath(__file__))
    
    css_file_path = os.path.join(frontend_dir, "bg.css")
    try:
        with open(css_file_path, "r") as f:
            css_content = f.read()
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass
    
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        resources_path = os.path.join(base_dir, "..", "Resources", "Placed_base64.txt")
        with open(resources_path, "r") as f:
            bg_image_data = f.read().strip()
        
        bg_data_url = f"data:image/jpeg;base64,{bg_image_data}"
        
        st.markdown(
            f'<style>:root {{ --bg-image-url: url("{bg_data_url}") }}</style>',
            unsafe_allow_html=True
        )
        
    except FileNotFoundError:
        # No background image - fallback CSS in bg.css handles this
        pass
