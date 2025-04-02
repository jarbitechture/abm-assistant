import os
import logging
import time
from hubspot import HubSpot
from hubspot.crm.contacts import SimplePublicObjectInput, ApiException as ContactApiException
from hubspot.crm.companies import SimplePublicObjectInput as CompanyInput, ApiException as CompanyApiException
from requests.exceptions import HTTPError, ConnectionError, Timeout, RequestException

# Constants
MAX_RETRIES = 3
RETRY_BACKOFF = 2  # seconds

# Use latest HubSpot token (override if needed)
HUBSPOT_API_KEY = "pat-na1-c68d0170-9a6b-4111-b47b-d7307b068541"
hubspot = HubSpot(access_token=HUBSPOT_API_KEY)

def create_or_update_contact(contact_data):
    retries = 0
    properties = {
        "email": contact_data["email"],
        "firstname": contact_data["name"].split()[0],
        "lastname": contact_data["name"].split()[-1],
        "phone": contact_data["phone"],
        "jobtitle": contact_data["title"],
        "company": contact_data.get("company"),
        "website": f"https://{contact_data['domain']}"
    }

    if contact_data.get("linkedin"):
        properties["hs_linkedin_url"] = contact_data["linkedin"]

    while retries < MAX_RETRIES:
        try:
            existing = hubspot.crm.contacts.basic_api.get_by_id(contact_data["email"], id_property="email")
            contact_id = existing.id
            hubspot.crm.contacts.basic_api.update(contact_id, SimplePublicObjectInput(properties=properties))
            logging.info(f"✅ Updated existing contact in HubSpot: {contact_id}")
            break
        except ContactApiException as e:
            if e.status == 404:
                try:
                    contact_input = SimplePublicObjectInput(properties=properties)
                    response = hubspot.crm.contacts.basic_api.create(contact_input)
                    logging.info(f"✅ Created contact in HubSpot: {response.id}")
                    break
                except Exception as inner_err:
                    logging.error(f"❌ Error creating contact: {inner_err}")
                    break
            else:
                logging.error(f"❌ Error checking/updating contact: {e}")
                break
        except Exception as e:
            logging.error(f"❌ Unknown error: {e}")
            break

        retries += 1
        time.sleep(RETRY_BACKOFF * (2 ** retries))

    if retries == MAX_RETRIES:
        logging.error("❌ Max retries reached. Failed to create/update contact in HubSpot.")

def create_target_account_in_hubspot(account_data):
    retries = 0
    properties = {
        "name": account_data["company"],
        "domain": account_data["domain"],
        "annualrevenue": account_data.get("revenue"),
        "website": f"https://{account_data['domain']}"
    }

    if not account_data.get("linkedin") and account_data.get("company"):
        slug = account_data["company"].lower().replace(" ", "")
        account_data["linkedin"] = f"https://www.linkedin.com/company/{slug}"

    if account_data.get("linkedin"):
        properties["linkedin_company_page"] = account_data["linkedin"]
        properties["hs_linkedin_handle"] = account_data["linkedin"].split("/")[-1]
        properties["linkedinbio"] = ""  # You may update this with scraped or enriched content if needed

    while retries < MAX_RETRIES:
        try:
            search = hubspot.crm.companies.search_api.do_search(
                public_object_search_request={
                    "filterGroups": [
                        {"filters": [{"propertyName": "domain", "operator": "EQ", "value": account_data["domain"]}]}
                    ]
                }
            )
            results = search.results
            if results:
                company_id = results[0].id
                hubspot.crm.companies.basic_api.update(company_id, CompanyInput(properties=properties))
                logging.info(f"✅ Updated company in HubSpot: {company_id}")
            else:
                company_input = CompanyInput(properties=properties)
                response = hubspot.crm.companies.basic_api.create(company_input)
                logging.info(f"✅ Created company in HubSpot: {response.id}")
            break

        except CompanyApiException as e:
            logging.error(f"❌ HubSpot company error: {e}")
            break

        except Exception as e:
            logging.error(f"❌ Unknown error creating/updating company: {e}")
            break

        retries += 1
        time.sleep(RETRY_BACKOFF * (2 ** retries))

    if retries == MAX_RETRIES:
        logging.error("❌ Max retries reached. Failed to create/update company in HubSpot.")
