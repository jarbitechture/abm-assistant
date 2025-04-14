# abm/hubspot_client.py

import logging
import time
from hubspot import HubSpot
from hubspot.crm.contacts import SimplePublicObjectInput, ApiException as ContactApiException
from hubspot.crm.companies import SimplePublicObjectInput as CompanyInput, ApiException as CompanyApiException
from requests.exceptions import RequestException # Import for broader network errors if needed

# --- CORRECT: Import the key loaded by config.py ---
# This assumes config.py successfully loads HUBSPOT_API_KEY from .env or secrets
try:
    from abm.config import HUBSPOT_API_KEY
except ImportError:
    logging.error("Failed to import HUBSPOT_API_KEY from abm.config. HubSpot client will not work.")
    HUBSPOT_API_KEY = None

# Constants
MAX_RETRIES = 2 # Reduced retries for faster feedback in prototype
RETRY_BACKOFF = 1 # seconds

# Initialize HubSpot client using the imported key
hubspot = None # Initialize as None
if HUBSPOT_API_KEY:
    try:
        hubspot = HubSpot(access_token=HUBSPOT_API_KEY)
        logging.info("HubSpot client initialized successfully.")
    except Exception as e:
        logging.error(f"Failed to initialize HubSpot client with provided key: {e}", exc_info=True)
else:
    logging.warning("HubSpot API Key not found or failed to import. HubSpot client is not initialized.")

# --- Helper Function to Check Client ---
def _is_hubspot_client_ready():
    """Checks if the HubSpot client is initialized."""
    if not hubspot:
        logging.error("HubSpot client is not initialized. Cannot perform operation.")
        return False
    return True

# --- Main Functions ---
def create_or_update_contact(contact_data: dict) -> dict:
    """
    Creates a new contact or updates an existing one in HubSpot based on email.
    Returns a status dictionary.
    """
    if not _is_hubspot_client_ready():
        return {"status": "error", "message": "HubSpot client not initialized"}

    retries = 0
    email = contact_data.get("email")
    if not email:
        logging.error("Cannot create/update contact: Email is missing from contact_data.")
        return {"status": "error", "message": "Contact email missing"}

    properties = {
        "email": email,
        "firstname": contact_data.get("name", "").split(" ")[0] if contact_data.get("name") else "",
        # Handle cases where name might only have one part
        "lastname": contact_data.get("name", "").split(" ")[-1] if " " in contact_data.get("name", "") else "",
        "phone": contact_data.get("phone"),
        "jobtitle": contact_data.get("title"),
        "company": contact_data.get("company"),
        "website": f"https://{contact_data['domain']}" if contact_data.get("domain") else None
    }
    # Add LinkedIn URL if available
    if contact_data.get("linkedin"):
        properties["hs_linkedin_url"] = contact_data["linkedin"]

    # Remove None properties which HubSpot API might reject
    properties = {k: v for k, v in properties.items() if v is not None}

    contact_input = SimplePublicObjectInput(properties=properties)

    while retries <= MAX_RETRIES:
        try:
            # Try to get contact by email to see if it exists
            # Note: Using email as the ID property for get_by_id
            existing_contact = hubspot.crm.contacts.basic_api.get_by_id(email, id_property="email", properties=["hs_object_id"])
            contact_id = existing_contact.id
            logging.info(f"Contact {email} exists (ID: {contact_id}). Attempting update.")
            hubspot.crm.contacts.basic_api.update(contact_id, contact_input)
            logging.info(f"✅ Updated existing contact in HubSpot: {email} (ID: {contact_id})")
            return {"status": "success", "action": "updated", "id": contact_id, "email": email}

        except ContactApiException as e:
            if e.status == 404:
                # Contact not found, try to create it
                logging.info(f"Contact {email} not found. Attempting create.")
                try:
                    create_response = hubspot.crm.contacts.basic_api.create(contact_input)
                    logging.info(f"✅ Created new contact in HubSpot: {email} (ID: {create_response.id})")
                    return {"status": "success", "action": "created", "id": create_response.id, "email": email}
                except ContactApiException as create_e:
                    logging.error(f"❌ Error creating contact {email}: {create_e}", exc_info=True)
                    # If create fails, break the loop for this attempt
                    return {"status": "error", "message": f"Failed to create contact: {create_e.status} {create_e.reason}"}
                except Exception as inner_err: # Catch other potential errors during create
                     logging.error(f"❌ Unexpected error creating contact {email}: {inner_err}", exc_info=True)
                     return {"status": "error", "message": f"Unexpected error creating contact: {inner_err}"}

            elif e.status == 429: # Rate limit
                 logging.warning(f"Rate limit hit for contacts. Retrying in {RETRY_BACKOFF * (2 ** retries)}s...")
                 # Fall through to retry logic
            else:
                logging.error(f"❌ HubSpot API error checking/updating contact {email}: {e}", exc_info=True)
                # Break loop on other API errors
                return {"status": "error", "message": f"API error checking/updating contact: {e.status} {e.reason}"}

        except RequestException as net_err: # Catch network errors
            logging.error(f"❌ Network error interacting with HubSpot contacts: {net_err}", exc_info=True)
            # Fall through to retry logic

        except Exception as e: # Catch other unexpected errors
            logging.error(f"❌ Unknown error during contact operation for {email}: {e}", exc_info=True)
            return {"status": "error", "message": f"Unknown error during contact operation: {e}"}

        # Retry logic
        retries += 1
        if retries <= MAX_RETRIES:
            time.sleep(RETRY_BACKOFF * (2 ** (retries -1))) # Exponential backoff

    logging.error(f"❌ Max retries reached for contact operation: {email}. Failed.")
    return {"status": "error", "message": "Max retries reached for contact operation"}


def create_target_account_in_hubspot(account_data: dict) -> dict:
    """
    Creates or updates a company in HubSpot based on domain.
    Returns a status dictionary.
    """
    if not _is_hubspot_client_ready():
        return {"status": "error", "message": "HubSpot client not initialized"}

    retries = 0
    domain = account_data.get("domain")
    if not domain:
        logging.error("Cannot create/update company: Domain is missing from account_data.")
        return {"status": "error", "message": "Company domain missing"}

    properties = {
        "name": account_data.get("company"),
        "domain": domain,
        "annualrevenue": account_data.get("revenue"),
        "website": f"https://{domain}" # Ensure website has protocol
    }
    # Add LinkedIn page if available
    if account_data.get("linkedin_company_page"): # Use a distinct key if available
        properties["linkedin_company_page"] = account_data["linkedin_company_page"]

    # Remove None properties
    properties = {k: v for k, v in properties.items() if v is not None}

    company_input = CompanyInput(properties=properties)

    while retries <= MAX_RETRIES:
        try:
            # Search for company by domain
            search_request = {
                "filterGroups": [{"filters": [{"propertyName": "domain", "operator": "EQ", "value": domain}]}],
                "properties": ["hs_object_id", "name", "domain"], # Request specific properties
                "limit": 1
            }
            search_result = hubspot.crm.companies.search_api.do_search(public_object_search_request=search_request)

            if search_result.results:
                # Company exists, update it
                company_id = search_result.results[0].id
                logging.info(f"Company {domain} exists (ID: {company_id}). Attempting update.")
                hubspot.crm.companies.basic_api.update(company_id, company_input)
                logging.info(f"✅ Updated existing company in HubSpot: {domain} (ID: {company_id})")
                return {"status": "success", "action": "updated", "id": company_id, "domain": domain}
            else:
                # Company not found, create it
                logging.info(f"Company {domain} not found. Attempting create.")
                create_response = hubspot.crm.companies.basic_api.create(company_input)
                logging.info(f"✅ Created new company in HubSpot: {domain} (ID: {create_response.id})")
                return {"status": "success", "action": "created", "id": create_response.id, "domain": domain}

        except CompanyApiException as e:
            if e.status == 429: # Rate limit
                 logging.warning(f"Rate limit hit for companies. Retrying in {RETRY_BACKOFF * (2 ** retries)}s...")
                 # Fall through to retry logic
            else:
                logging.error(f"❌ HubSpot API error during company operation for {domain}: {e}", exc_info=True)
                # Break loop on other API errors
                return {"status": "error", "message": f"API error during company operation: {e.status} {e.reason}"}

        except RequestException as net_err: # Catch network errors
            logging.error(f"❌ Network error interacting with HubSpot companies: {net_err}", exc_info=True)
            # Fall through to retry logic

        except Exception as e: # Catch other unexpected errors
            logging.error(f"❌ Unknown error during company operation for {domain}: {e}", exc_info=True)
            return {"status": "error", "message": f"Unknown error during company operation: {e}"}

        # Retry logic
        retries += 1
        if retries <= MAX_RETRIES:
            time.sleep(RETRY_BACKOFF * (2 ** (retries -1)))

    logging.error(f"❌ Max retries reached for company operation: {domain}. Failed.")
    return {"status": "error", "message": "Max retries reached for company operation"}