# tests/test_sales_copilot.py

import pytest
from unittest.mock import patch
from abm.sales_copilot import summarize_deal_context

def test_summarize_deal_context():
    mock_contact = {
        "name": "Jane Doe",
        "email": "jane@example.com",
        "company": "Acme Corp",
        "domain": "acme.com",
        "title": "Marketing Director",
        "revenue": 10000000,
        "linkedin": "https://linkedin.com/in/janedoe"
    }

    with patch("abm.sales_copilot.openai.ChatCompletion.create") as mock_create:
        mock_create.return_value = {
            "choices": [{"message": {"content": "Test sales summary output."}}]
        }
        result = summarize_deal_context(mock_contact)

    assert result == "Test sales summary output."
    mock_create.assert_called_once()
