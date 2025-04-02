# abm/target_account_creator.py

from typing import Dict

REVENUE_THRESHOLD = 3000000


def create_target_account(enriched: Dict) -> Dict:
    """
    Decide if the enriched company qualifies as a target account.
    """
    print(f"🧠 Creating TARGET ACCOUNT for {enriched['company']} ({enriched['domain']})")

    if enriched["revenue"] >= REVENUE_THRESHOLD:
        return {
            "status": "targeted",
            "account": {
                "company": enriched["company"],
                "domain": enriched["domain"],
                "revenue": enriched["revenue"],
                "contact_name": enriched["name"],
                "contact_email": enriched["email"],
            }
        }
    else:
        return {"status": "skipped", "reason": "Low revenue"}
