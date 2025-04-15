import streamlit as st
import requests
import logging
import os
import time
from dotenv import load_dotenv

# --- Load environment variables ---
load_dotenv()

# --- Logging config ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | line %(lineno)d | %(message)s"
)
logger = logging.getLogger("Dashboard")

# --- Constants ---
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# --- Page setup ---
st.set_page_config(page_title="ABM Pipeline Dashboard", layout="centered")
st.title("🎯 ABM Pipeline Interface")
st.markdown("Submit a contact to **enrich**, evaluate, and trigger the **ABM pipeline**.")

# --- Health Check ---
with st.expander("🔍 Check API Health", expanded=False):
    if st.button("Run Health Check"):
        try:
            r = requests.get(f"{API_BASE_URL}/health", timeout=5)
            if r.status_code == 200:
                st.success("✅ API is healthy.")
                logger.info("Health check passed.")
            else:
                st.warning(f"⚠️ API unhealthy (Status: {r.status_code})")
        except Exception as e:
            st.error(f"❌ Could not reach API: {e}")
            logger.exception("Health check failed")

# --- Contact Form ---
st.subheader("📬 Contact Submission")

with st.form("abm_form"):
    name = st.text_input("Full Name", "Jane Doe")
    email = st.text_input("Email", "jane.doe@example.com")
    company = st.text_input("Company", "Example Corp")
    domain = st.text_input("Domain", "example.com")
    title = st.text_input("Job Title", "VP of Marketing")
    phone = st.text_input("Phone", "+1 555-123-4567")
    use_crew = st.checkbox("Enable CrewAI Agents", value=True)

    col1, col2 = st.columns(2)
    with col1:
        enrich_submit = st.form_submit_button("✨ Enrich Contact Only")
    with col2:
        pipeline_submit = st.form_submit_button("🚀 Run ABM Pipeline")

contact_data = {
    "name": name,
    "email": email,
    "company": company,
    "domain": domain,
    "title": title,
    "phone": phone,
}

# --- Enrichment Only Mode ---
if enrich_submit:
    try:
        logger.info(f"Submitting to /enrich: {contact_data}")
        res = requests.post(f"{API_BASE_URL}/enrich", json=contact_data, timeout=10)
        if res.status_code == 200:
            enriched = res.json()
            st.success("✅ Enrichment successful!")
            st.json(enriched)
            logger.info("Enrichment completed.")
        else:
            st.error(f"❌ Enrichment failed: {res.status_code}")
            st.text(res.text)
    except Exception as e:
        st.error(f"Error during enrichment: {e}")
        logger.exception("Enrichment call failed")

# --- Pipeline Run Mode ---
if pipeline_submit:
    try:
        logger.info(f"Submitting to /run-pipeline: {contact_data} | CrewAI: {use_crew}")
        res = requests.post(
            f"{API_BASE_URL}/run-pipeline",
            json=contact_data,
            params={"use_crew": str(use_crew).lower()},
            timeout=10
        )
        if res.status_code == 202:
            result = res.json()
            st.success(f"✅ Pipeline accepted for {result['contact_email']}")
            st.info(result["message"])
            logger.info("Pipeline queued successfully.")

            # Simulate polling logic (mock-ready)
            with st.spinner("⏳ Waiting for pipeline to complete..."):
                time.sleep(2)  # simulate delay
                st.success("✅ Pipeline processing completed.")
                st.markdown("🔄 Add real-time polling with DB or job ID tracking if needed.")
        else:
            st.error(f"❌ Pipeline failed: {res.status_code}")
            st.text(res.text)
    except Exception as e:
        st.error(f"Pipeline request error: {e}")
        logger.exception("Pipeline request failed")
