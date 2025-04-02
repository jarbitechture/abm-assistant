import pytest
from enrichment import enrich_contact_data

def test_enrichment():
    contact = {"domain": "acme.com"}
    enriched = enrich_contact_data(contact)
    assert enriched["company"] is not None
