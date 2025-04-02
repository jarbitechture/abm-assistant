# main.py

import argparse
from abm.config import OPENAI_API_KEY  # .env is already loaded inside config.py
from abm.run_abm_pipeline import run_abm_pipeline

# Debugging print (optional)
print("🔐 OpenAI Key Loaded:", OPENAI_API_KEY[:5] + "***")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--use-crew", action="store_true", help="Enable CrewAI agent-based execution")
    args = parser.parse_args()

    contact = {
        "name": "Jane Doe",
        "email": "jane@example.com",
        "company": "Acme Corp",
        "domain": "acme.com",
        "title": "Marketing Director",
        "phone": "123-456-7890"
    }

    print("🚀 Starting ABM Pipeline...")
    run_abm_pipeline(trigger_contact=contact, use_crew=args.use_crew)
