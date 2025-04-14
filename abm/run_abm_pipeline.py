# abm/run_abm_pipeline.py

import logging
import json
from typing import Dict, Any

# --- Default value in case imports fail ---
MODULES_LOADED = False
IMPORT_ERROR_MESSAGE = "Unknown import error" # Store message outside function scope

# --- Use relative imports for modules within the 'abm' package ---
try:
    from .config import TARGET_ACCOUNT_REVENUE_THRESHOLD
    from .enrichment import enrich_contact_data
    # from .scraper import scrape_summary_for_domain # Usually called within enrichment

    # --- CORRECTED IMPORT NAME ---
    from .target_account_creator import evaluate_target_account # <-- Correct name used
    # --- END CORRECTION ---

    from .hubspot_client import create_or_update_contact, create_target_account_in_hubspot
    from .sales_copilot import summarize_deal_context
    from .crew import TargetAccountCrew
    MODULES_LOADED = True
    logging.info("Successfully imported ABM modules in run_abm_pipeline.")
except ImportError as import_error: # Give the exception a name here
    logging.basicConfig(level=logging.ERROR)
    IMPORT_ERROR_MESSAGE = str(import_error) # Store the specific error message
    logging.critical(f"Failed to import required ABM modules in run_abm_pipeline: {IMPORT_ERROR_MESSAGE}", exc_info=True)
    # Define the function even if imports fail
    def run_abm_pipeline(trigger_contact: dict, use_crew: bool = False) -> Dict[str, Any]:
         # Corrected fallback return (Fixes NameError)
         return {"status": "failed", "reason": f"Failed to load critical pipeline modules during import phase: {IMPORT_ERROR_MESSAGE}"}

# Get a logger specific to this module
logger = logging.getLogger(__name__)

# --- Main Pipeline Function ---
# Check MODULES_LOADED in case imports failed above
if MODULES_LOADED:
    def run_abm_pipeline(trigger_contact: dict, use_crew: bool = False) -> Dict[str, Any]:
        """
        Executes the Account-Based Marketing pipeline for a given trigger contact.
        Args: trigger_contact, use_crew flag. Returns: Result dictionary.
        """
        logger.info(f"🚀 Starting ABM Pipeline logic for: {trigger_contact.get('email', 'N/A')}")
        logger.info(f"CrewAI Execution Enabled: {use_crew}")
        pipeline_result: Dict[str, Any] = { # Initialize result dict
            "status": "started", "reason": None, "enriched_contact": None,
            "targeting_status": None, "targeting_reason": None, "account_data": None,
            "hubspot_contact_result": None, "hubspot_company_result": None,
            "summary": None, "summary_error": None, "crew_outputs": None, "crew_error": None
        }

        # 1. Enrichment Stage
        try:
            logger.info("Step 1: Starting Enrichment...")
            enriched = enrich_contact_data(trigger_contact)
            pipeline_result["enriched_contact"] = enriched
            logger.info(f"🔍 Enrichment completed.")
            # (Optional detailed logging of enriched data)
        except Exception as e: # Catch any enrichment error
            logger.error("❌ Failed during enrichment", exc_info=True)
            pipeline_result.update({"status": "failed", "reason": f"Enrichment error: {e}"})
            return pipeline_result # Stop pipeline on enrichment failure

        # 2. Target Evaluation Stage
        try:
            logger.info("Step 2: Evaluating Target Account...")
            # --- CORRECTED FUNCTION CALL ---
            account_decision = evaluate_target_account(enriched) # <-- Correct name used
            # --- END CORRECTION ---
            status = account_decision.get('status', 'error')
            reason = account_decision.get('reason', 'No reason provided.')
            pipeline_result["targeting_status"] = status
            pipeline_result["targeting_reason"] = reason
            logger.info(f"📊 Target Evaluation Result: Status={status}, Reason={reason}")

            # --- Process based on evaluation status ---
            if status == "targeted":
                account_data = account_decision.get("account")
                if not account_data:
                     logger.error("❌ Evaluation status 'targeted' but no account data.")
                     pipeline_result.update({"targeting_status": "error", "targeting_reason": "Internal error: Missing account data."})
                else:
                     pipeline_result["account_data"] = account_data
                     logger.info("Account targeted. Proceeding...")

                     # 3. HubSpot Operations
                     try:
                         logger.info("Step 3: Syncing with HubSpot...")
                         contact_res = create_or_update_contact(enriched)
                         pipeline_result["hubspot_contact_result"] = contact_res
                         logger.info(f"HubSpot Contact Result: {contact_res}")
                         company_res = create_target_account_in_hubspot(account_data)
                         pipeline_result["hubspot_company_result"] = company_res
                         logger.info(f"HubSpot Company Result: {company_res}")
                         # (Optional: Log overall HubSpot success/warning)
                     except Exception as e:
                         logger.error("❌ HubSpot operations failed unexpectedly", exc_info=True)
                         # (Optional: Update result dict with generic error)

                # 4. AI Summarization (Runs if targeted)
                logger.info("Step 4: Generating AI Deal Summary...")
                try:
                    summary_list = summarize_deal_context(enriched)
                    summary_or_error = summary_list[0]
                    if summary_or_error.startswith("❌"):
                        logger.error(f"Failed generating GPT summary: {summary_or_error}")
                        pipeline_result["summary_error"] = summary_or_error
                        pipeline_result["summary"] = None
                    else:
                        logger.info(f"\n📝 GPT Summary generated:\n{summary_or_error}")
                        pipeline_result["summary"] = summary_or_error
                        pipeline_result["summary_error"] = None
                except Exception as e:
                     logger.error("❌ Failed generating GPT summary (unexpected error)", exc_info=True)
                     pipeline_result["summary_error"] = f"Unexpected summary error: {e}"
                     pipeline_result["summary"] = None

                # 5. CrewAI Execution (Runs if targeted and use_crew=True)
                if use_crew:
                    logger.info("Step 5: Executing with CrewAI agents...")
                    try:
                        if not enriched: raise ValueError("Enriched data missing for CrewAI.")
                        crew_builder = TargetAccountCrew(contact=enriched)
                        crew, tasks = crew_builder.build()
                        if crew and tasks:
                            logger.info("Crew built, kicking off...")
                            crew_output = crew.kickoff()
                            logger.info("Crew kickoff completed.")
                            strategist_out = tasks[0].output.raw_output if len(tasks) > 0 and tasks[0].output else "N/A"
                            analyst_out = tasks[1].output.raw_output if len(tasks) > 1 and tasks[1].output else "N/A"
                            logger.info(f"📈 Crew Strategist Output:\n{strategist_out}")
                            logger.info("📊 Crew Analyst Output (Attempting JSON parse):")
                            try: # Try parsing analyst output
                                if isinstance(analyst_out, str) and analyst_out.strip():
                                    clean_analyst_out = analyst_out.strip().removeprefix("```json").removesuffix("```").strip()
                                    if clean_analyst_out: logger.info(f"\n{json.dumps(json.loads(clean_analyst_out), indent=2)}")
                                    else: logger.info("(Empty Output)")
                                else: logger.info(f"(Raw/Empty Output): {analyst_out}")
                            except Exception as json_err:
                                logger.warning(f"Could not parse Analyst output as JSON: {json_err}")
                                logger.info(f"(Raw/Non-JSON Output):\n{analyst_out}")
                            pipeline_result["crew_outputs"] = {"strategist": strategist_out, "analyst": analyst_out}
                            logger.info("✅ CrewAI execution finished.")
                        else:
                            logger.error("❌ CrewAI build failed. Skipping kickoff.")
                            pipeline_result["crew_error"] = "Failed to build CrewAI."
                    except Exception as e:
                        logger.error("❌ CrewAI execution failed", exc_info=True)
                        pipeline_result["crew_error"] = f"CrewAI error: {e}"
                else:
                     logger.info("Step 5: CrewAI execution skipped (use_crew=False).")

            elif status == "skipped":
                 pipeline_result.update({"status": "skipped"})
                 logger.info(f"🚫 Pipeline skipped. Reason: {reason}")
            else: # Handle "error" status from evaluation
                 pipeline_result.update({"status": "error", "reason": f"Target evaluation failed: {reason}"})
                 logger.error(f"❌ Target evaluation failed: {reason}")

        except Exception as e:
             logger.error("❌ Failed during target evaluation or subsequent steps", exc_info=True)
             if pipeline_result.get("status") not in ["failed", "error"]:
                 pipeline_result.update({"status": "failed", "reason": f"Pipeline error after enrichment: {e}"})

        # --- Final Log and Return ---
        final_status = pipeline_result.get("status", "unknown")
        if final_status == "started": final_status = pipeline_result.get("targeting_status", "unknown")

        logger.info(f"✅ Pipeline Finished for {trigger_contact.get('email', 'N/A')}. Final Status: {final_status}")
        pipeline_result["status"] = final_status
        return pipeline_result
# --- End of function definition ---