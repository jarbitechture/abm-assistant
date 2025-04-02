# abm/sales_copilot.py

from typing import Dict
from openai import OpenAI
from abm.config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

def summarize_deal_context(contact: Dict) -> str:
    if not OPENAI_API_KEY:
        return "❌ OpenAI API key not found."

    try:
        prompt = (
            f"Generate a sales summary for {contact['name']} ({contact['title']}) at {contact['company']} "
            f"with {contact['employees']} employees and ${contact['revenue']:,} in revenue. "
            f"Company Summary: {contact['summary']}"
        )

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a sales assistant helping craft B2B outreach."},
                {"role": "user", "content": prompt},
            ]
        )
        return [response.choices[0].message.content.strip()]

    except Exception as e:
        return f"❌ GPT Summary Error: {str(e)}"
