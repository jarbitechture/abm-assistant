# abm/enrichment.py

from typing import Dict
import random
from abm.scraper import scrape_summary_for_domain

def enrich_contact_data(contact: Dict) -> Dict:
    domain = contact.get("domain", "example.com")

    linkedin_url = f"https://linkedin.com/in/{contact['name'].replace(' ', '').lower()}"
    scraped_summary = scrape_summary_for_domain(domain)

    return {
        **contact,
        "linkedin": linkedin_url,
        "revenue": random.choice([2000000, 5000000, 10000000]),
        "employees": random.choice([50, 200, 500]),
        "summary": scraped_summary,
        "sources": {
            "linkedin": "Generated from name via LinkedIn format",
            "summary": f"Scraped from {domain}",
            "revenue": "Mocked (e.g., from Clearbit)",
            "employees": "Mocked (e.g., from Clearbit)"
        }
    }
