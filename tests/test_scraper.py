# tests/test_scraper.py

from abm.scraper import scrape_summary_for_domain

def test_scrape_summary_for_known_domains():
    assert "Acme Corp" in scrape_summary_for_domain("acme.com")
    assert "cloud solutions" in scrape_summary_for_domain("example.com")
    assert "CRM platform" in scrape_summary_for_domain("hubspot.com")

def test_scrape_summary_for_unknown_domain():
    domain = "unknowncompany.com"
    result = scrape_summary_for_domain(domain)
    assert domain in result
    assert "B2B SaaS company" in result
