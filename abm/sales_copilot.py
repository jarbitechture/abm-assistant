# abm/sales_copilot.py

import logging
from typing import Dict, List # Use List for return type hint

# --- CORRECT: Import the key and model loaded by config.py ---
try:
    from abm.config import OPENAI_API_KEY, OPENAI_SUMMARY_MODEL
except ImportError:
    logging.error("Failed to import OpenAI config from abm.config. Sales Copilot will not work.")
    OPENAI_API_KEY = None
    OPENAI_SUMMARY_MODEL = "gpt-3.5-turbo" # Fallback model if config fails

# --- Initialize OpenAI Client ---
# Use the official 'openai' library V1.x+ syntax
try:
    from openai import OpenAI, RateLimitError, APIError, APITimeoutError
    client = None
    if OPENAI_API_KEY:
        client = OpenAI(api_key=OPENAI_API_KEY, max_retries=1, timeout=20.0) # Set timeout, low retries
        logging.info(f"OpenAI client initialized successfully for model: {OPENAI_SUMMARY_MODEL}")
    else:
        logging.warning("OpenAI API Key not found or failed to import. OpenAI client is not initialized.")
except ImportError:
    logging.error("OpenAI library not found. Please install it (`pip install openai`).")
    client = None
except Exception as e:
    logging.error(f"Failed to initialize OpenAI client: {e}", exc_info=True)
    client = None


def summarize_deal_context(contact: Dict) -> List[str]:
    """
    Generates a sales summary using OpenAI based on contact details.
    Returns a list containing the summary string or an error message.
    """
    if not client:
        logging.error("Cannot generate summary: OpenAI client is not initialized.")
        return ["❌ OpenAI client not initialized. Check API Key."]

    # Basic check for essential contact info needed for the prompt
    required_fields = ["name", "title", "company", "employees", "revenue", "summary"]
    missing_fields = [field for field in required_fields if field not in contact or not contact[field]]
    if missing_fields:
        msg = f"❌ Cannot generate summary: Missing required contact fields: {', '.join(missing_fields)}"
        logging.warning(msg)
        # Return error message in the expected list format
        return [msg]

    # Construct the prompt
    try:
        # Format revenue nicely if it's a number
        revenue_str = f"${contact['revenue']:,}" if isinstance(contact.get('revenue'), (int, float)) else str(contact.get('revenue', 'N/A'))
        prompt = (
            f"Generate a concise B2B sales summary and potential talking points for outreach to "
            f"{contact['name']} ({contact.get('title', 'N/A')}) at {contact['company']}. "
            f"The company has approximately {contact.get('employees', 'N/A')} employees and revenue around {revenue_str}. "
            f"Focus on potential needs based on this company profile and their business: {contact.get('summary', 'No company summary available.')}"
        )
        logging.info(f"Generating summary for {contact['email']} using model {OPENAI_SUMMARY_MODEL}")
    except Exception as e:
        logging.error(f"Error constructing prompt for {contact.get('email', 'N/A')}: {e}", exc_info=True)
        return [f"❌ Error creating prompt: {e}"]


    try:
        response = client.chat.completions.create(
            model=OPENAI_SUMMARY_MODEL, # Use model from config
            messages=[
                {"role": "system", "content": "You are a helpful B2B sales assistant providing concise summaries and talking points for account executives."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.5, # Slightly creative but still factual
            max_tokens=250, # Limit length
            n=1, # Generate one response
            stop=None # Let the model decide when to stop
        )
        # Extract the content
        summary = response.choices[0].message.content.strip()
        logging.info(f"Successfully generated summary for {contact['email']}")
        # Return summary in a list as per original potential design
        return [summary]

    except RateLimitError:
        logging.error("OpenAI API rate limit exceeded.")
        return ["❌ OpenAI API rate limit exceeded. Please try again later."]
    except APITimeoutError:
         logging.error("OpenAI API request timed out.")
         return ["❌ OpenAI API request timed out."]
    except APIError as api_err:
        # Handle other OpenAI API errors (e.g., server errors, invalid requests)
        logging.error(f"OpenAI API error: {api_err}", exc_info=True)
        return [f"❌ OpenAI API Error: {api_err}"]
    except Exception as e:
        # Catch any other unexpected errors during the API call
        logging.error(f"An unexpected error occurred calling OpenAI: {e}", exc_info=True)
        return [f"❌ Unexpected error during AI summary generation: {e}"]