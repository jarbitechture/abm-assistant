# tests/test_hubspot_client.py

import pytest
import logging
from unittest.mock import patch, MagicMock
from abm.hubspot_client import create_or_update_contact, create_target_account_in_hubspot
from dotenv import load_dotenv
import os

@pytest.fixture(scope="session", autouse=True)
def load_test_env():
    load_dotenv()
    hubspot_key = os.getenv("HUBSPOT_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    assert hubspot_key, "Missing HUBSPOT_API_KEY in .env"
    assert openai_key, "Missing OPENAI_API_KEY in .env"
    assert len(hubspot_key) >= 20, "HUBSPOT_API_KEY must be at least 20 characters"
    assert len(openai_key) >= 30, "OPENAI_API_KEY must be at least 30 characters"

@pytest.fixture(autouse=True)
def enable_logging():
    logging.getLogger().setLevel(logging.DEBUG)

@patch("abm.hubspot_client.hubspot")
def test_create_or_update_contact_create(mock_hubspot):
    contact_data = {
        "name": "Jane Doe",
        "email": "jane@example.com",
        "company": "Test Corp",
        "domain": "test.com",
        "title": "Marketing Director",
        "phone": "123-456-7890",
        "linkedin": "https://linkedin.com/in/janedoe"
    }

    mock_hubspot.crm.contacts.basic_api.get_by_id.side_effect = Exception("404")
    mock_hubspot.crm.contacts.basic_api.create.return_value.id = "123"

    create_or_update_contact(contact_data)
    mock_hubspot.crm.contacts.basic_api.create.assert_called_once()

@patch("abm.hubspot_client.hubspot")
def test_create_target_account_create(mock_hubspot):
    account_data = {
        "company": "Test Corp",
        "domain": "test.com",
        "revenue": 5000000,
        "linkedin": "https://linkedin.com/company/testcorp"
    }

    mock_hubspot.crm.companies.search_api.do_search.return_value.results = []
    mock_hubspot.crm.companies.basic_api.create.return_value.id = "456"

    create_target_account_in_hubspot(account_data)
    mock_hubspot.crm.companies.basic_api.create.assert_called_once()

@patch("abm.hubspot_client.hubspot")
def test_create_target_account_update(mock_hubspot):
    account_data = {
        "company": "Test Corp",
        "domain": "test.com",
        "revenue": 5000000,
        "linkedin": "https://linkedin.com/company/testcorp"
    }

    mock_company = MagicMock()
    mock_company.id = "456"
    mock_hubspot.crm.companies.search_api.do_search.return_value.results = [mock_company]

    create_target_account_in_hubspot(account_data)
    mock_hubspot.crm.companies.basic_api.update.assert_called_once()

@patch("abm.hubspot_client.hubspot")
def test_create_or_update_contact_update(mock_hubspot):
    contact_data = {
        "name": "Jane Doe",
        "email": "jane@example.com",
        "company": "Test Corp",
        "domain": "test.com",
        "title": "Marketing Director",
        "phone": "123-456-7890"
    }

    mock_contact = MagicMock()
    mock_contact.id = "123"
    mock_hubspot.crm.contacts.basic_api.get_by_id.return_value = mock_contact

    create_or_update_contact(contact_data)
    mock_hubspot.crm.contacts.basic_api.update.assert_called_once()
