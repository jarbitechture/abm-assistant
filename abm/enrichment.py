# abm/enrichment.py

import logging
import random
from typing import Dict, Optional
# Use relative import for scraper
from .scraper import scrape_summary_for_domain

logger = logging.getLogger(__name__)

def _generate_mock_linkedin_url(name: Optional[str]) -> Optional[str]:
    """Generates a plausible mock LinkedIn profile URL from a name."""
    if not name:
        return None
    # Basic cleaning for URL slug generation
    slug = name.lower().replace(' ', '').replace('.', '').strip()
    if not slug:
        return None
    return f"https://linkedin.com/in/{slug}"

def _generate_mock_company_linkedin_url(company: Optional[str]) -> Optional[str]:
     """Generates a plausible mock LinkedIn company page URL from a company name."""
     if not company:
         return None
     # Very basic slug generation - real enrichment is much more complex
     slug = company.lower().replace(' ', '-').replace('.', '').replace(',', '').replace('&', 'and').strip('-')
     if not slug:
         return None
     return f"https://www.linkedin.com/company/{slug}"


def enrich_contact_data(contact: Dict) -> Dict:
    """
    Enriches contact data with mocked information (revenue, employees, LinkedIn, summary).

    Args:
        contact: Dictionary with initial contact details (must include 'domain').

    Returns:
        An enriched dictionary including original and mocked data.

    Raises:
        ValueError: If the input contact dictionary is missing the 'domain' key.
    """
    logger.debug(f"Starting enrichment for contact: {contact.get('email', 'N/A')}")
    domain = contact.get("domain")
    if not domain:
         logger.error("Enrichment failed: Input contact dictionary must include a 'domain' key.")
         raise ValueError("Contact dictionary must include a 'domain' key for enrichment.")

    company_name = contact.get("company")
    contact_name = contact.get("name")

    try:
        scraped_summary = scrape_summary_for_domain(domain)
        logger.debug(f"Mock scraped summary for {domain}: {scraped_summary[:100]}...")
    except Exception as e:
        logger.warning(f"Mock scraping failed for domain {domain}: {e}. Using default summary.")
        scraped_summary = f"Summary data unavailable for {domain}."

    # Mocked data generation
    mock_revenue = random.choice([2000000, 5000000, 10000000, 15000000, 25000000])
    mock_employees = random.choice([50, 200, 500, 1000, 2500])
    mock_linkedin_person = _generate_mock_linkedin_url(contact_name)
    mock_linkedin_company = _generate_mock_company_linkedin_url(company_name)

    enriched_data = {
        **contact, # Include all original contact fields
        "linkedin": mock_linkedin_person,
        "revenue": mock_revenue,
        "employees": mock_employees,
        "summary": scraped_summary,
        "linkedin_company_page": mock_linkedin_company,
        # Clearly list the sources of the enriched data
        "sources": {
            "linkedin": f"Mocked: Generated from name ('{contact_name}')" if mock_linkedin_person else "Mocked: Name unavailable",
            "summary": f"Mocked: Scraped from {domain}",
            "revenue": f"Mocked: Random value ({mock_revenue:,})",
            "employees": f"Mocked: Random value ({mock_employees})",
            "linkedin_company_page": f"Mocked: Generated from company name ('{company_name}')" if mock_linkedin_company else "Mocked: Company name unavailable"
        }
    }
    logger.info(f"Enrichment completed for contact: {contact.get('email', 'N/A')}")
    logger.debug(f"Enriched data fields added: revenue, employees, linkedin, summary, linkedin_company_page")
    return enriched_data