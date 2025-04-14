# dashboard.py
import streamlit as st
import `dashboard.py` file.

This version includes:
*   The checkbox to enable/disable CrewAI.
*   Calls `run_abm_pipeline` with logging
import traceback # To show detailed errors during debugging
import json # For displaying the `use_crew` flag.
*   Displays all sections of the pipeline results, including the CrewAI output or errors conditionally.
*   Uses the `pipeline JSON and parsing CrewAI output

# --- Setup Logging ---
# Configure once_output` dictionary structure returned by the updated `run_abm_pipeline.py`.

```python
# dashboard.py
import streamlit as st
import logging
, preferably at the start.
# Streamlit has its own logging, but this helpsimport traceback # To show detailed errors during debugging
import json # To parse Crew modules using standard logging.
logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(name)s:%(lineno)d -AI JSON output

# --- Setup Logging ---
# Note: Streamlit manages %(levelname)s] - %(message)s", force=True)
logger = logging its own logging, basicConfig might have limited effect
# but good practice for.getLogger(__name__)

# --- Import your logic functions directly ---
# Wrap imports in try-except to catch issues early, especially config loading
try:
 modules called from here.
logging.basicConfig(level=logging.INFO, format="%(asctime    from abm.config import OPENAI_API_KEY, HUBSPOT_API_KEY, TARGET_ACCOUNT_REVENUE_THRESHOLD
    from ab)s - [%(name)s:%(lineno)d - %(levelname)s] - %(messagem.run_abm_pipeline import run_abm_pipeline #)s")
logger = logging.getLogger(__name__)

# --- Import Import the main pipeline function
    MODULES_LOADED = True
    logger.info(" your logic functions directly ---
# Wrap imports in try-except to catch issuesSuccessfully imported ABM modules.")
except ImportError as e:
    logger.critical early, especially config loading
MODULES_LOADED = False
KEYS_READY = False
OPENAI_API_KEY = None
HUBSPOT_API_KEY = None
TARGET_ACCOUNT_REVENUE_THRESHOLD = 3000000 # Default(f"Failed to import ABM modules: {e}", exc_info=True)
    # fallback

try:
    from abm.config import OPENAI_API_KEY, HUBSPOT_ Set flag and display error in UI later
    MODULES_LOADED = False
    API_KEY, TARGET_ACCOUNT_REVENUE_THRESHOLD
    from abm.enrichment import enrich_contact_data
    from abm.OPENAI_API_KEY = None # Ensure these are None if import fails
    HUBSPOT_scraper import scrape_summary_for_domain # Ensure this is available if needed directlyAPI_KEY = None
    TARGET_ACCOUNT_REVENUE_THRESHOLD =
    from abm.target_account_creator import create_target_account
    from abm.hubspot_client import create_or_ 0 # Default value
except Exception as e: # Catch other potential initupdate_contact, create_target_account_in_hubspot
     errors (e.g., config loading)
    logger.critical(f"Failedfrom abm.sales_copilot import summarize_deal_context
    from abm.run_abm_pipeline import run_abm_pipeline # during initial setup (maybe config loading?): {e}", exc_info=True)
    MODULES_LOADED = False
    OPENAI_API_KEY = None
    HUBSPOT_API_KEY Import the main pipeline runner
    # CrewAI import happens within run_abm_pipeline if needed
    MODULES_LOADED = True
    KEYS_READY = bool(OPENAI_ = None
    TARGET_ACCOUNT_REVENUE_THRESHOLD = 0


API_KEY and HUBSPOT_API_KEY) # Check if keys# --- Streamlit UI ---
st.set_page_config(layout="wide") # Use wider layout
st.title("⚡ ABM Pipeline Dashboard were loaded by config
except ImportError as e:
    logger.error(f"Failed ⚡")

# Display Key Status in Sidebar
st.sidebar.subheader(" to import ABM modules: {e}", exc_info=True)
    # DisplayStatus & Config")
if MODULES_LOADED:
    st.sidebar.success("✅ Modules Loaded")
    st.sidebar.info(f"OpenAI Key: {'✅ Loaded' if OPENAI_API_KEY else '❌ Missing'}")
    st.sidebar error prominently if modules fail to load
    st.error(f"Critical Error: Failed to load application modules. Check logs. Error: {e}")
except Exception as e: #.info(f"HubSpot Key: {'✅ Loaded' if HUBSPOT_API_ Catch config loading errors too
    logger.error(f"Failed during initial setup (maybeKEY else '❌ Missing'}")
    st.sidebar.info(f config loading?): {e}", exc_info=True)
    st.error"Target Revenue: ${TARGET_ACCOUNT_REVENUE_THRESHOLD:,}")
    KEYS_READY = bool(OPENAI_API_KEY and HUBS(f"Critical Error: Failed during initial setup. Check logs. Error: {e}")


# --- Streamlit UI ---
st.set_page_config(layout="wide")POT_API_KEY)
    if not KEYS_READY:
         st.sidebar.error("Missing API keys! Check .env or Streamlit secrets.")
else
st.title("⚡ ABM Pipeline Dashboard ⚡")

# Display:
    st.sidebar.error("❌ Modules Failed to Load. Check Logs Key Status in Sidebar
st.sidebar.subheader("⚙️ Status & Config")
if MODULE.")
    KEYS_READY = False


# --- Input Form ---
with st.form("abm_input_form"):
    st.subheaderS_LOADED:
    st.sidebar.success("✅ Modules Loaded")
    st("Enter Contact Details")
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Name", "Test Contact")
        email = st.text_input("Email", "test.sidebar.info(f"OpenAI Key: {'✅ Loaded' if OPENAI_API_KEY@streamlit.io") # Use a domain likely to resolve
        company = else '❌ Missing'}")
    st.sidebar.info(f"HubSpot Key: {'✅ Loaded' if HUBSPOT_API_KEY else '❌ Missing'}")
    st.sidebar.info(f"Target Revenue: ${TARGET_ACCOUNT st.text_input("Company Name", "Streamlit")
    with col2:
        domain =_REVENUE_THRESHOLD:,}")
    if not KEYS_READY:
 st.text_input("Company Domain", "streamlit.io")
        title = st         st.sidebar.error("Missing API keys! Check .env file locally or Streamlit secrets.")
else.text_input("Title", "App Creator")
        phone = st:
    st.sidebar.error("❌ Modules Failed to Load")


.text_input("Phone", "N/A") # Optional

    # CrewAI Checkbox
    use_crew_ai = st.checkbox("🤖# --- Input Form ---
with st.form("abm_input_form"):
    st.subheader("Enter Contact Details")
    col1, col2 = st.columns(2)
    with col1:
        name = st.text Enable CrewAI Agents?", value=False, help="Run additional analysis using AI_input("Name", "Test Contact")
        # Use a domain likely to resolve for scraping test
        email = st.text_input("Email", "test@ agents (requires more time and tokens).")

    # Submit Button - Disable if modulesstreamlit.io")
        company = st.text_input("Company Name", "Streamlit")
    with col2:
        domain = st.text_input("Company failed or keys missing
    submitted = st.form_submit_button("🚀 Run AB Domain", "streamlit.io")
        title = st.text_input("Title", "M Pipeline", disabled=(not MODULES_LOADED or not KEYS_READY))

# --- Pipeline Execution Logic ---
if submitted:
    # BasicApp Creator")
        phone = st.text_input("Phone", "N/A")

    st.markdown("---") # Separator
    use_crew_ validation before running
    if not all([name, email, company, domainai = st.checkbox("Enable CrewAI Agents?", value=False, help="Run additional, title]):
        st.warning("Please fill in all required fields (Name, Email, Company, Domain, Title).")
    elif not MODULES_LOADED:
          analysis using AI agents (slower, requires more tokens).") # Add checkbox

    submitted = st.form_submit_button("🚀 Run ABM Pipelinest.error("Cannot run pipeline: Core application modules failed to load. Check logs.")
    elif not KEYS", disabled=(not MODULES_LOADED or not KEYS_READY))

#_READY:
         st.error("Cannot run pipeline: Missing OpenAI or HubSpot API key --- Pipeline Execution Logic ---
if submitted:
    if not MODULES_LOADED or not KEYS_READY:
         st.error("Cannot run pipeline. Fix loading errors or missing API keys shown in the sidebar.")
    else:
        st.markdown("---") # Separator
        st.subheader("Pipeline Execution Results")
        contact. Check sidebar and secrets.")
    else:
        st.markdown("---")_input = {
            "name": name, "email": email, # Separator
        st.subheader("Pipeline Execution Results")
        contact_input = {
            "name": name, "email": email, "company": company,
            "domain": domain, "title": title, "phone": phone
 "company": company,
            "domain": domain, "title": title, "phone": phone
        }

        # Use columns for better layout of results
                }

        # Use columns for better layout of results
        res_col1, res_res_col1, res_col2 = st.columns(2)
        pipeline_output = None # Initialize output variable

        try:
            # ---col2 = st.columns(2)
        pipeline_failed = False # Flag for critical failures

        try:
            # --- Call the pipeline runner Call the pipeline function ---
            with st.spinner(f"Running pipeline ---
            with st.spinner(f"Running pipeline (CrewAI: {' {'with CrewAI...' if use_crew_ai else '...'}"):
                loggerEnabled' if use_crew_ai else 'Disabled'})..."):
                pipeline_output = run_abm_pipeline(contact_input, use_crew=use.info(f"Calling run_abm_pipeline for {email},_crew_ai)
            # --- End Call ---

            logger.debug use_crew={use_crew_ai}")
                pipeline_output =(f"Pipeline Output Received: {pipeline_output}") # Log the full output run_abm_pipeline(contact_input, use_crew=use_crew_ai)
                logger.info(f"Pipeline function returned. Status: {pipeline_output.get('status')}")

            # --- Display for debugging

            # --- Display Results from pipeline_output dictionary ---

            # 1. Enrichment Display Results from pipeline_output dictionary ---

            # Overall Status
            st.metric
            with res_col1:
                st.markdown("#### 1. Enrichment & Scraping")
                enriched_data = pipeline_output.get("enriched_("Overall Pipeline Status", pipeline_output.get('status', 'Unknown').capitalize(),contact")
                if enriched_data:
                    st.success("Step delta=pipeline_output.get('reason'), delta_color="off")

            # Enrichment 1 Done.")
                    with st.expander("View Enriched Data", & Scraping Results
            with res_col1:
                st.markdown expanded=False):
                        st.json(enriched_data)
                else:
                    st.warning("Enrichment data not found in results.")
                    if("#### 1. Enrichment & Scraping")
                enriched_data = pipeline_output.get pipeline_output.get("status") == "failed" and "Enrichment" in pipeline_output("enriched_contact")
                if enriched_data:
                    with st.expander("View.get("reason", ""):
                         st.error(f"Reason Enriched Data", expanded=False):
                        st.json(enriched_data)
                    st.success("Enrichment step completed.")
                else:
                    : {pipeline_output.get('reason')}")
                         pipeline_failed = True #st.warning("Enrichment data not found in results.")

            # Targeting Enrichment failure is critical

            # 2. Targeting Display
            if not pipeline_ Results
            with res_col1:
                st.markdown("####failed:
                with res_col1:
                    st.markdown("#### 2. Targeting Decision 2. Targeting Decision")
                targeting_status = pipeline_output.get")
                    status = pipeline_output.get("targeting_status", "Unknown("targeting_status", "Unknown")
                targeting_reason = pipeline_output.get("targeting_reason")
                    reason = pipeline_output.get("targeting_reason", "")
                    st.success("Step 2 Done.")
                    st.metric("Targeting Status", status", "")
                st.metric("Targeting Status", targeting_status.capitalize(),.capitalize(), reason)
                    if status == "error":
                         st.error( delta=targeting_reason, delta_color="off")

            # HubSpotf"Targeting Error: {reason}")
                         # Decide if targeting error stops Results (only show if attempted)
            hubspot_contact_res = pipeline_output.get(" flow - likely yes
                         # pipeline_failed = True

            # --- Subsequenthubspot_contact_result")
            hubspot_company_res = pipeline_output.get("hubspot_company_result")
            if hubspot_contact_res or hubspot_company_res:
                with res_col2:
 steps only if targeted and no critical failure ---
            if not pipeline_failed and pipeline_output.                    st.markdown("#### 3. HubSpot Update")
                    if hubspot_contactget("targeting_status") == "targeted":
                # 3. HubSpot Display_res:
                        st.write(f"**Contact ({hubspot_contact_res.get
                with res_col2:
                    st.markdown("#### 3. HubSpot Update Status")
                    contact_res = pipeline_output.get("hubspot_contact_result")
                    company_res = pipeline_output.get('email', 'N/A')}):** Status=`{hubspot_contact_res.("hubspot_company_result")

                    if contact_res:
                        if contact_res.get("status") == "success":
                            st.get('status')}`, Action=`{hubspot_contact_res.get('action', 'N/A')}`, Msg=`{hubspot_contact_res.get('message', '')write(f"✅ Contact ({contact_res.get('action', 'processed}`")
                    else:
                        st.write("**Contact:** No result')}): Success (ID: {contact_res.get('id', 'N/A') captured.")
                    if hubspot_company_res:
                         st.write(f"**Company})")
                        else:
                            st.warning(f"⚠️ Contact: ({hubspot_company_res.get('domain', 'N/A')}):** Status=`{hubspot_company_res.get('status') {contact_res.get('status', 'unknown')} - {contact_res.get}`, Action=`{hubspot_company_res.get('action', 'N/A')}`, Msg=`('message', 'No details')}")
                    else:
                        st.write{hubspot_company_res.get('message', '')}`")
                    else:
                         st.write("**Company:** No result captured.")

            # AI Summary Results
            with res_col("⚪ Contact: No result captured.")

                    if company_res:
                         2:
                st.markdown("#### 4. AI Sales Summary")
                aiif company_res.get("status") == "success":
                            st.write_summary = pipeline_output.get("summary")
                ai_summary_error = pipeline_output(f"✅ Company ({company_res.get('action', 'processed')}): Success (ID: {company_res.get('id', 'N/A')}).get("summary_error")
                if ai_summary_error:
                    st.error(f"Summary Error: {ai_summary_error}")
                elif ai_summary:")
                         else:
                            st.warning(f"⚠️ Company: {company_res.get('
                    with st.expander("View AI Summary", expanded=True):
status', 'unknown')} - {company_res.get('message', 'No details')}")
                    else:
                        st.write("⚪ Company                        st.markdown(ai_summary)
                else:
                    #: No result captured.")

                # 4. AI Summary Display
                with res_col2:
                     st.markdown("#### 4. AI Sales Summary")
                     summary = Only show info if targeting was successful but summary is missing
                    if pipeline_output pipeline_output.get("summary")
                     summary_error = pipeline_.get("targeting_status") == "targeted":
                        st.infooutput.get("summary_error")
                     if summary_error:
                         st.warning(f"⚠️ Summary Generation Error: {summary_error}")
                     ("AI summary was not generated or found in results.")

            # CrewAI Results (elif summary:
                         st.success("Step 4 Done.")
                         st.only show if run)
            if use_crew_ai:
                st.markdown("markdown(summary)
                     else:
                         st.info("No AI summary---") # Separator before CrewAI results
                st.subheader("🤖 generated or captured.")

                # 5. CrewAI Display (only if run CrewAI Agent Results")
                crew_outputs = pipeline_output.get("crew)
                if use_crew_ai:
                    with res_col2: #_outputs")
                crew_error = pipeline_output.get("crew_error")

                if Display in the second column
                        st.markdown("#### 5. CrewAI Agent crew_error:
                    st.error(f"CrewAI Execution Error: {crew_error}")
 Results")
                        crew_outputs = pipeline_output.get("crew_outputs")
                        crew_error = pipeline_output.get("crew_error")

                        if                elif crew_outputs:
                    st.success("CrewAI execution reported success.")
                    # Display Strategist Output
                    with st.expander("Strategist Output"): crew_error:
                            st.error(f"CrewAI Error: {crew_error}")

                        st.text(crew_outputs.get("strategist", "N/A"))
                    # Display Analyst Output (Attempt JSON Parse)
                    with st.exp                        elif crew_outputs:
                            st.success("Step 5 Done.")
                            with st.expander("Strategist Output", expanded=False):
                                st.text(crew_outputs.get("strategist", "N/A"))
                            with st.expander("Analyst Outputander("Analyst Output (Attempted JSON)"):
                        analyst_raw = crew_outputs.get("analyst", "N/A")
 (Attempted JSON)", expanded=False):
                                analyst_raw = crew_outputs.get("analyst", "N/A")
                                try:
                                    # Try cleaning and parsing JSON again for display
                                    if isinstance                        try:
                            # Try cleaning and parsing JSON again for display
                            if isinstance(analyst_(analyst_raw, str) and analyst_raw.strip():
                                         raw, str) and analyst_raw.strip():
                                 # Basicclean_analyst_out = analyst_raw.strip().removeprefix("```json").removesuffix("```").strip()
                                         # Handle cleaning of potential markdown fences
                                 clean_analyst_out = analyst_raw.strip(). potential empty string after cleaning
                                         if clean_analyst_out:
                                             parsedremoveprefix("```json").removesuffix("```").strip()
                                 #_json = json.loads(clean_analyst_out)
                                             st.json(parsed_json)
                                         else:
                                Handle potential escape sequences if needed (less common now)
                                 # clean              st.text("(Empty Output)")
                                    else:
                                         st.text_analyst_out = bytes(clean_analyst_out, "utf-8").decode("unicode_escape")
                                 parsed_json = json.loads(clean(analyst_raw) # Display raw if not string or empty
                               _analyst_out)
                                 st.json(parsed_json except Exception as json_e:
                                     logger.warning(f"Dashboard) # Display as interactive JSON
                            else:
                                 st.text(analyst_raw) # Display raw if not string or empty
                        except Exception as json_ex failed to parse analyst JSON: {json_e}")
                                     st.text(analyst_raw) # Display raw if parsing fails
                        else:
                            st.info:
                             logger.warning(f"Dashboard failed to parse analyst JSON: {json_ex}")
("CrewAI ran, but no specific output was captured in results.")

            elif not pipeline_failed and pipeline_output.get("targeting_status") == "                             st.text(analyst_raw) # Display raw text if parsing fails
                elseskipped":
                 res_col2.info(f"➡️ Account skipped. Reason:
                    # Check if targeting status might explain missing output
                    if pipeline_output.get: {pipeline_output.get('targeting_reason', 'N/A')}")
                 res("targeting_status") == "targeted":
                         st.info("CrewAI was_col2.info("HubSpot, AI Summary, and CrewAI steps not enabled, but no specific output was captured in the results.")
                    else:
 executed.")

            st.success("Pipeline Finished.")
            if not pipeline_failed and pipeline_output.                         st.info("CrewAI was enabled, but likely did not run due to targeting status.")


get("targeting_status") != "error":
                st.balloons()

        except Exception as e:
            st.error("💥 A critical error occurred during the dashboard            # --- Final Success Indication ---
            final_status = pipeline_output.get's pipeline execution:")
            st.exception(e) # Shows the full traceback in the Streamlit('status', 'unknown')
            if final_status not in ['failed', 'error']:
                 st.balloons()

        except Exception as e:
            # Catch errors happening *outside* the run_abm_pipeline function call app
            logger.critical("Unhandled Dashboard Pipeline Error", exc_info=True)

# Add a footer or separator
st.markdown("---")