import argparse
import logging
import json
from abm.config import OPENAI_API_KEY, HUBSPOT_API_KEY
from abm.enrichment import enrich_contact_data
from abm.scraper import scrape_summary_for_domain
from abm.target_account_creator import create_target_account
from abm.hubspot_client import create_or_update_contact, create_target_account_in_hubspot
from abm.sales_copilot import summarize_deal_context
from abm.crew import TargetAccountCrew

# Override HUBSPOT_API_KEY for latest token
HUBSPOT_API_KEY = "pat-na1-c68d0170-9a6b-4111-b47b-d7307b068541"

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def run_abm_pipeline(trigger_contact: dict, use_crew: bool = False):
    logging.info("🚀 Starting ABM Pipeline...")

    try:
        enriched = enrich_contact_data(trigger_contact)
        enriched["summary"] = scrape_summary_for_domain(enriched["domain"])
        logging.info(f"🔍 Enriched Contact: {enriched}")
    except Exception as e:
        logging.error("❌ Failed during enrichment", exc_info=True)
        return

    logging.info("📚 Data Sources Used:")
    for field, source in enriched.get("sources", {}).items():
        logging.info(f" - {field.capitalize()}: {source}")

    if enriched["revenue"] < 5000000:
        logging.warning("❌ Contact/company does not meet ABM revenue threshold.")
        return

    try:
        account_data = create_target_account(enriched)
        logging.info(f"🏢 Target Account Created: {account_data}")

        create_or_update_contact(enriched)
        create_target_account_in_hubspot(account_data["account"])
    except Exception as e:
        logging.error("❌ HubSpot operations failed", exc_info=True)
        return

    logging.info("🧠 GPT Deal Summary:")
    try:
        summary_with_sources = "\n".join(summarize_deal_context(enriched)) + "\n\nSources:\n"
        for field, source in enriched.get("sources", {}).items():
            summary_with_sources += f"- {field.capitalize()}: {source}\n"
        logging.info(summary_with_sources)
    except Exception as e:
        logging.error("❌ Failed generating GPT summary", exc_info=True)

    if use_crew:
        logging.info("🧠 Executing with CrewAI agents...")
        try:
            crew, tasks = TargetAccountCrew(contact=enriched).build()
            crew.kickoff()

            # Strategist output (as string)
            logging.info(f"📈 Strategist Output: {tasks[0].output}")

            # Analyst output: pretty-print if JSON
            analyst_output = tasks[1].output
            try:
                parsed_json = json.loads(analyst_output)
                formatted_json = json.dumps(parsed_json, indent=2)
                logging.info(f"📊 Analyst Output (JSON):\n{formatted_json}")
            except Exception:
                logging.info(f"📊 Analyst Output: {analyst_output}")

        except Exception as e:
            logging.error("❌ CrewAI execution failed", exc_info=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--use-crew", action="store_true", help="Enable CrewAI agent-based execution")
    args = parser.parse_args()

    mock_contact = {
        "name": "Jane Doe",
        "email": "jane@example.com",
        "company": "Acme Corp",
        "domain": "acme.com",
        "title": "Marketing Director",
        "phone": "123-456-7890",
    }

    run_abm_pipeline(trigger_contact=mock_contact, use_crew=args.use_crew)
