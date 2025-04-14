# streamlit_app.py
import streamlit as st
import requests
import os
import json
import logging # Add logging

# Configure basic logging for Streamlit app (optional)
# logging.basicConfig(level=logging.INFO, format="%(asctime)s - [Streamlit] - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


# --- Configuration ---
# Best practice: Read from environment variable set for the Streamlit process,
# falling back to a default that should match your API's host/port.
# Ensure this matches where your FastAPI app is running.
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000") # Default if env var not set
ENRICH_ENDPOINT = f"{API_BASE_URL}/enrich"
PIPELINE_ENDPOINT = f"{API_BASE_URL}/run-pipeline" # Use the async endpoint
HEALTH_ENDPOINT = f"{API_BASE_URL}/health"

# --- Helper Functions ---
def check_api_health():
    """Checks if the backend API is reachable."""
    try:
        response = requests.get(HEALTH_ENDPOINT, timeout=5) # Add timeout
        response.raise_for_status()
        return response.json().get("status") == "ok"
    except requests.exceptions.RequestException as e:
        logger.error(f"API Health Check failed: {e}")
        # Display error within the function or return False for caller to handle
        # st.error(f"❌ Backend API ({API_BASE_URL}) is unreachable. Please ensure the API server is running. Error: {e}")
        return False
    except Exception as e:
         logger.error(f"Unexpected error during API Health Check: {e}")
         # st.error(f"An unexpected error occurred during API health check: {e}")
         return False

# --- Streamlit App Layout ---
st.set_page_config(layout="wide", page_title="ABM Contact Processor")
st.title("✨ ABM Contact Processor ✨")

# Sidebar for API Info and Health Check
st.sidebar.header("⚙️ API Status")
st.sidebar.info(f"API Endpoint: `{API_BASE_URL}`")
api_status_placeholder = st.sidebar.empty() # Placeholder for status message

if st.sidebar.button("Check API Health", key="health_check_button"):
    with st.spinner("Checking API status..."):
        if check_api_health():
            api_status_placeholder.success("✅ API is reachable and healthy.")
        else:
            api_status_placeholder.error(f"❌ API ({API_BASE_URL}) unreachable.")


st.sidebar.markdown("---")
st.sidebar.header("ℹ️ About")
st.sidebar.info("This app triggers an ABM pipeline. Enter contact details and choose an action.")


# --- Main Area ---

st.header("1. Enter Contact Details")
st.markdown("Fill in the required (*) contact information below.")

# --- Input Form ---
# Use columns for better layout and provide clear labels/help text
# Ensure ALL fields needed by the API's ContactInput model are here.
with st.form("contact_form"):
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Full Name*", help="Contact's full name (e.g., Jane Doe)")
        email = st.text_input("Email*", help="Contact's valid business email address")
        company = st.text_input("Company Name*", help="The company the contact works for")

    with col2:
        domain = st.text_input("Company Domain*", help="Company website domain (e.g., acme.com)")
        title = st.text_input("Job Title", help="(Optional) Contact's job title")
        phone = st.text_input("Phone Number", help="(Optional) Contact's phone number, any format")

    st.markdown("""_* Required fields_""")

    # Form submission button
    submitted = st.form_submit_button("Load Contact Data")

    if submitted:
        # Store form data in session state after successful submission
        # Basic validation (FastAPI backend does the main validation)
        if not all([name, email, company, domain]):
            st.error("Please fill in all required fields (*) before submitting.")
        else:
            st.session_state['contact_payload'] = {
                "name": name, "email": email, "company": company,
                "domain": domain, "title": title or None, "phone": phone or None
            }
            st.success("Contact data loaded. Choose an action below.")
            # Clear previous results when new data is loaded
            st.session_state.pop('enrichment_result', None)
            st.session_state.pop('pipeline_status', None)
            logger.info(f"Contact data loaded into session state for {email}")


# --- Actions ---
st.header("2. Process Contact")

# Only show actions if contact data is loaded
if 'contact_payload' in st.session_state:
    st.info(f"Processing for: **{st.session_state['contact_payload']['email']}**")
    payload = st.session_state['contact_payload']

    col_actions1, col_actions2 = st.columns(2)

    with col_actions1:
        if st.button("🧠 Enrich Contact Only", key="enrich_button", use_container_width=True):
            logger.info(f"Enrich action triggered for {payload['email']}")
            try:
                with st.spinner("Calling Enrichment API..."):
                    response = requests.post(ENRICH_ENDPOINT, json=payload, timeout=30) # Add timeout
                    response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
                    data = response.json()
                    # Store result in session state for display
                    st.session_state['enrichment_result'] = data
                    st.session_state.pop('pipeline_status', None) # Clear old pipeline status
                    st.success("Enrichment successful!")
                    logger.info(f"Enrichment successful for {payload['email']}")

            except requests.exceptions.RequestException as e:
                 logger.error(f"Enrichment API Request Failed: {e}")
                 st.error(f"API Request Failed: {e}")
                 # Try to display more detailed error from API response
                 if e.response is not None:
                     try:
                          error_detail = e.response.json().get('detail', e.response.text)
                          st.error(f"API Error Details: {error_detail}")
                     except json.JSONDecodeError:
                          st.error(f"API Error Content (non-JSON): {e.response.text}")
            except Exception as e:
                 logger.error(f"Unexpected error during enrichment call: {e}", exc_info=True)
                 st.error(f"An unexpected error occurred: {e}")

    with col_actions2:
         # Allow selection of CrewAI usage
         use_crew = st.checkbox("Use CrewAI Agents?", value=False, key="crew_toggle")

         if st.button("🚀 Run Full ABM Pipeline", key="pipeline_button", use_container_width=True):
            logger.info(f"Pipeline action triggered for {payload['email']} (Use Crew: {use_crew})")
            try:
                with st.spinner("Triggering ABM Pipeline task in background..."):
                    # Pass use_crew as a query parameter
                    params = {"use_crew": use_crew}
                    response = requests.post(PIPELINE_ENDPOINT, json=payload, params=params, timeout=15) # Shorter timeout for acceptance
                    response.raise_for_status() # Check for 4xx/5xx errors

                    # Expecting 202 Accepted for background task
                    if response.status_code == 202:
                         status_data = response.json()
                         st.session_state['pipeline_status'] = status_data # Store acceptance message
                         st.session_state.pop('enrichment_result', None) # Clear old enrichment result
                         st.success(f"✅ {status_data.get('message', 'Pipeline task accepted!')}")
                         st.info("The pipeline is running in the background. Check API server logs for details and completion status.")
                         logger.info(f"Pipeline task accepted by API for {payload['email']}")
                    else:
                         # Handle unexpected success codes if API logic changes
                         st.warning(f"Pipeline endpoint returned unexpected status {response.status_code}. Expected 202.")
                         st.json(response.json())
                         logger.warning(f"Pipeline endpoint for {payload['email']} returned {response.status_code}, Response: {response.text}")


            except requests.exceptions.RequestException as e:
                 logger.error(f"Pipeline API Request Failed: {e}")
                 st.error(f"API Request Failed: {e}")
                 if e.response is not None:
                     try:
                          error_detail = e.response.json().get('detail', e.response.text)
                          st.error(f"API Error Details: {error_detail}")
                     except json.JSONDecodeError:
                          st.error(f"API Error Content (non-JSON): {e.response.text}")
            except Exception as e:
                 logger.error(f"Unexpected error during pipeline call: {e}", exc_info=True)
                 st.error(f"An unexpected error occurred: {e}")

else:
    st.warning("Please load contact data using the form above before processing.")


# --- Display Results Area ---
st.header("3. Results / Status")

# Display Enrichment results if available
if 'enrichment_result' in st.session_state:
    st.subheader("Enrichment Output:")
    st.json(st.session_state['enrichment_result'])

# Display Pipeline status if available
elif 'pipeline_status' in st.session_state:
    st.subheader("Pipeline Status:")
    # Display the acceptance message from the API response
    status_data = st.session_state['pipeline_status']
    st.success(f"Status: `{status_data.get('status', 'N/A')}` | Email: `{status_data.get('contact_email', 'N/A')}`")
    st.info(f"Message: {status_data.get('message', 'N/A')}")
    st.warning("ℹ️ Check API server logs for detailed pipeline execution progress and final results.")

else:
    st.info("Results from 'Enrich Contact' or status from 'Run Pipeline' will appear here after performing an action.")