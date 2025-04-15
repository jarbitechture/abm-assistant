# app.py

import streamlit as st
import requests

st.set_page_config(page_title="Express + Streamlit GUI")

st.title("Express Server Health Checker")

api_host = st.text_input("Express Server URL", "http://localhost:3000")

if st.button("Check Server"):
    try:
        response = requests.get(api_host)
        st.success(f"✅ Response: {response.text}")
    except requests.exceptions.ConnectionError:
        st.error("❌ Could not connect to the server.")
