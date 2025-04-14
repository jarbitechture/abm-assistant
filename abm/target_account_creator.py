# abm/target_account_creator.py
import logging  # <-- Import the standard logging library
from typing import Dict
# --- Remove 'logger' from this import ---
from .config import TARGET_ACCOUNT_REVENUE_THRESHOLD # <-- Use relative import for config

# --- Get a logger instance specific to this module ---
logger = logging.getLogger(__name__)

# --- Keep the evaluate_target_account function as refined previously ---
def evaluate_target_account(enriched: Dict) -> Dict:
    """
    Decide if the enriched company qualifies as a target account based on revenue.
    """
    # Use logger.info instead of print
    logger.info(f"Evaluating TARGET ACCOUNT for {enriched.get('company', 'N/A')} ({enriched.get('domain', 'N/A')})")

    # Ensure revenue exists and is comparable
    revenue = enriched.get("revenue")
    if revenue is None:
        logger.warning("Revenue data missing, cannot evaluate for target account.")
        # Return an error or specific skipped status
        return {"status": "error", "reason": "Missing revenue data"}

    if revenue >= TARGET_ACCOUNT_REVENUE_THRESHOLD:
        # Ensure all required keys exist before accessing
        account_details = {
            "company": enriched.get("company"),
            "domain": enriched.get("domain"),
            "revenue": revenue, # Use the validated revenue
            "contact_name": enriched.get("name"),
            "contact_email": enriched.get("email"),
            "linkedin_company_page": enriched.get("linkedin_company_page"),
            "employees": enriched.get("employees")
        }
        # Check if essential keys are missing
        if not all([account_details["company"], account_details["domain"]]):
            logger.error("Missing essential company data (company, domain) for target evaluation.")
            return {"status": "error", "reason": "Missing essential company data (company, domain) for target evaluation"}

        logger.info(f"Company {account_details['company']} QUALIFIED as target account.")
        return {
            "status": "targeted",
            "account": account_details
        }
    else:
        logger.info(f"Company {enriched.get('company', 'N/A')} SKIPPED. Reason: Low revenue ({revenue} < {TARGET_ACCOUNT_REVENUE_THRESHOLD})")
        return {"status": "skipped", "reason": f"Low revenue ({revenue} < {TARGET_ACCOUNT_REVENUE_THRESHOLD})"}