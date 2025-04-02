# abm/scraper.py

def scrape_summary_for_domain(domain: str) -> str:
    """
    Mocked scraping logic. Returns a fake summary for the domain.
    Replace with real scraper integration later.
    """
    summaries = {
        "acme.com": "Acme Corp is a leader in marketing automation, helping clients scale with data-driven insights.",
        "example.com": "Example Inc. provides innovative cloud solutions for small businesses.",
        "hubspot.com": "HubSpot offers a powerful CRM platform for scaling marketing and sales operations."
    }
    return summaries.get(domain, f"{domain} is a B2B SaaS company specializing in growth enablement.")
