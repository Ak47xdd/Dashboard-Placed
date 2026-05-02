import streamlit as st

def set_bg_image():
    with open("Resources/Placed_base64.txt", "r") as f:
        bg_image_data = f.read().strip()
    
    bg_data_url = f"data:image/jpeg;base64,{bg_image_data}"
    
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("{bg_data_url}");
            background-attachment: fixed;
            background-size: cover;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )