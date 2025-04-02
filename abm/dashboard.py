import streamlit as st
import requests

st.title("ABM Pipeline Dashboard")

name = st.text_input("Name")
email = st.text_input("Email")
domain = st.text_input("Company Domain")

if st.button("Enrich"):
    payload = {"name": name, "email": email, "domain": domain}
    response = requests.post("http://localhost:8000/enrich", json=payload)
    if response.ok:
        data = response.json()
        st.json(data)
    else:
        st.error("Enrichment failed")
