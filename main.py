# main.py

import argparse
import logging
import json # Import json for printing results

# Attempt relative imports if running as part of the 'abm' package
# This structure assumes you run `python main.py` from the project root directory
# where the 'abm' folder resides.
try:
    from abm.config import OPENAI_API_KEY # Check if key is loaded (optional)
    from abm.run_abm_pipeline import run_abm_pipeline
except ImportError as e:
    # Provide more context if import fails
    print(f"ImportError: {e}")
    print("Ensure you are running `python main.py` from the project root directory")
    print("containing the 'abm' package and that your PYTHONPATH is set correctly if needed.")
    # Fallback for running script directly maybe? Less ideal.
    # print("Failed relative import, trying direct...")
    # from config import OPENAI_API_KEY
    # from run_abm_pipeline import run_abm_pipeline
    exit(1) # Exit if imports fail, as the script cannot continue


# --- Configure logging ONCE at the application entry point ---
# Use a format that includes module name and line number for better debugging
log_format = "%(asctime)s - [%(name)s:%(lineno)d - %(levelname)s] - %(message)s"
logging.basicConfig(level=logging.INFO, format=log_format, force=True)
# force=True might be needed if libraries (like HubSpot's SDK) also try to call basicConfig.
# Ideally, library logging is configured differently, but force=True can override.
# --- End of basicConfig call ---

# Get a logger specific to this main script (optional, but good practice)
logger = logging.getLogger(__name__)

# Optional: Check if key seems loaded without printing it
# Log this *after* basicConfig is set up
if OPENAI_API_KEY and len(OPENAI_API_KEY) > 5:
     logger.info("OpenAI Key seems loaded (via config module).")
else:
     logger.warning("OpenAI Key not found or seems invalid in config module.")


# The main execution block
if __name__ == "__main__":
    # basicConfig() should have already run by the time this block executes

    parser = argparse.ArgumentParser(description="Run the ABM Pipeline for a mock contact via CLI.")
    parser.add_argument("--use-crew", action="store_true", help="Enable CrewAI agent-based execution")
    # Example: Add arguments to override mock contact details
    parser.add_argument("--email", type=str, help="Override mock contact email")
    parser.add_argument("--domain", type=str, help="Override mock contact domain")
    parser.add_argument("--name", type=str, help="Override mock contact name")
    parser.add_argument("--company", type=str, help="Override mock contact company")

    args = parser.parse_args()

    # Default mock contact
    contact = {
        "name": "Bob The Builder",
        "email": "bob@fixit.com",
        "company": "FixIt Construction",
        "domain": "fixit.com",
        "title": "Chief Fixing Officer",
        "phone": "555-FIX-ITUP"
    }

    # Override mock data if CLI args provided
    if args.name:
        contact["name"] = args.name
    if args.email:
        contact["email"] = args.email
    if args.company:
         contact["company"] = args.company
    if args.domain:
        contact["domain"] = args.domain
        if not args.company: # Auto-derive company if only domain given
            contact["company"] = args.domain.split('.')[0].capitalize() + " Services"


    logger.info(f"🚀 Starting ABM Pipeline via CLI for contact: {contact.get('email', 'N/A')}")
    logger.info(f"Using CrewAI agents: {args.use_crew}")
    logger.debug(f"Contact details being used: {json.dumps(contact, indent=2)}")

    try:
        # Run the pipeline function imported from the abm package
        result = run_abm_pipeline(trigger_contact=contact, use_crew=args.use_crew)

        # Log the final result structure clearly
        logger.info("🏁 Pipeline execution finished via CLI.")
        logger.info("--- Final Pipeline Result ---")
        # Pretty print the result dictionary to the console using standard print
        print(f"\nFinal Result:\n{json.dumps(result, indent=4)}\n")
        logger.info("--- End of Result ---")

    except Exception as e:
        # Catch any exception that might bubble up from the pipeline if not handled internally
        logger.critical(f"❌ Pipeline execution failed with unhandled exception: {e}", exc_info=True)