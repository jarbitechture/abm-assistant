# abm/abm_api.py

import logging
from typing import Optional, Dict, Any # Added Dict, Any

from fastapi import FastAPI, HTTPException, BackgroundTasks # Removed Depends as not used
from pydantic import BaseModel, EmailStr, Field, HttpUrl # Added Field, HttpUrl

# Use relative imports for internal modules
from .run_abm_pipeline import run_abm_pipeline
from .enrichment import enrich_contact_data
# Import config value if needed (e.g., for display or checks)
from .config import API_BASE_URL, OPENAI_API_KEY, HUBSPOT_API_KEY

# Configure logging for the API module
# Assumes basicConfig called ONCE at application entry point (e.g., uvicorn startup)
logger = logging.getLogger(__name__)

# --- API Setup ---
app = FastAPI(
    title="ABM Pipeline API",
    description="API for enriching contacts and running the Account-Based Marketing (ABM) processing pipeline.",
    version="0.2.0", # Increment version
    # Optional: Add contact info, license info, etc.
    # contact={"name": "Support Team", "email": "support@example.com"},
)


# --- Input Models (Pydantic) ---
class ContactInput(BaseModel):
    """Input model for contact details required by the API."""
    name: str = Field(..., description="Contact's full name", examples=["Jane Doe"])
    email: EmailStr = Field(..., description="Contact's valid business email address", examples=["jane.doe@acme.com"])
    company: str = Field(..., description="Name of the company the contact works for", examples=["Acme Corporation"])
    domain: str = Field(..., description="Company website domain", examples=["acme.com"])
    title: Optional[str] = Field(None, description="Contact's job title (Optional)", examples=["Marketing Director"])
    phone: Optional[str] = Field(None, description="Contact's phone number (Optional)", examples=["+1-555-123-4567"])

    # Add example for OpenAPI docs
    class Config:
        # Use model_config for Pydantic v2
        model_config = {
            "json_schema_extra": {
                 "example": {
                    "name": "John Smith",
                    "email": "john.smith@example.com",
                    "company": "Example Inc.",
                    "domain": "example.com",
                    "title": "VP of Sales",
                    "phone": "123-456-7890"
                }
            }
        }


# --- Output Models (Pydantic) ---
class EnrichmentOutput(BaseModel):
    """Output model for the enrichment endpoint."""
    # Define the expected structure of the enriched data
    name: str
    email: EmailStr
    company: str
    domain: str
    title: Optional[str] = None
    phone: Optional[str] = None
    linkedin: Optional[HttpUrl | str] = None # Allow string if generation fails or is just text
    revenue: Optional[int] = None
    employees: Optional[int] = None
    summary: Optional[str] = None
    linkedin_company_page: Optional[HttpUrl | str] = None # Allow string
    sources: Dict[str, str] = {}

    class Config:
        # Use model_config for Pydantic v2
         model_config = {
            "json_schema_extra": {
                 "example": {
                    "name": "John Smith",
                    "email": "john.smith@example.com",
                    "company": "Example Inc.",
                    "domain": "example.com",
                    "title": "VP of Sales",
                    "phone": "123-456-7890",
                    "linkedin": "https://linkedin.com/in/johnsmith",
                    "revenue": 10000000,
                    "employees": 250,
                    "summary": "Example Inc. provides innovative solutions.",
                    "linkedin_company_page": "https://linkedin.com/company/example-inc",
                    "sources": {
                        "linkedin": "Mocked: Generated", "summary": "Mocked: Scraped",
                        "revenue": "Mocked: Random", "employees": "Mocked: Random",
                        "linkedin_company_page": "Mocked: Generated"
                    }
                 }
            }
         }

class PipelineAcceptResponse(BaseModel):
    """Response model when a pipeline task is accepted."""
    status: str = Field("accepted", description="Indicates the task was accepted for processing.")
    message: str = Field(..., description="User-friendly message about task queuing.")
    contact_email: EmailStr = Field(..., description="Email of the contact being processed for reference.")


# --- API Endpoints ---

@app.on_event("startup")
async def startup_event():
    """Log essential info on API startup."""
    logger.info("--- ABM API Starting Up ---")
    logger.info(f"API Base URL (from config): {API_BASE_URL}")
    # Check if keys appear loaded based on config module's attempt
    openai_status = "Yes" if OPENAI_API_KEY else "NO - OpenAI features disabled"
    hubspot_status = "Yes" if HUBSPOT_API_KEY else "NO - HubSpot features disabled"
    logger.info(f"OpenAI Key Loaded: {openai_status}")
    logger.info(f"HubSpot Key Loaded: {hubspot_status}")
    logger.info("API Ready to accept requests.")

@app.get("/health", summary="Health Check", tags=["System"])
async def health_check():
    """Basic health check endpoint to verify the API is running."""
    logger.debug("Health check endpoint called.")
    # Could add checks here for DB connection, external services' basic reachability if needed
    return {"status": "ok"}


@app.post("/enrich",
          response_model=EnrichmentOutput, # Use the defined output model
          summary="Enrich Contact Data",
          tags=["Processing"])
async def enrich_api(contact: ContactInput):
    """
    Takes basic contact information and returns enriched data using (mocked) services.
    """
    logger.info(f"Received enrichment request for: {contact.email}")
    try:
        # Convert Pydantic model to dict for the enrichment function
        # Use model_dump() for Pydantic v2+
        enriched_data = enrich_contact_data(contact.model_dump())
        logger.info(f"Enrichment successful for: {contact.email}")
        # Pydantic will automatically validate the output against EnrichmentOutput
        return enriched_data
    except ValueError as ve: # Catch specific known errors (e.g., missing domain)
         logger.warning(f"Enrichment validation error for {contact.email}: {ve}")
         raise HTTPException(status_code=400, detail=str(ve)) # 400 Bad Request
    except Exception as e:
        logger.error(f"Unexpected error during enrichment for {contact.email}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error during enrichment.")


@app.post("/run-pipeline",
          response_model=PipelineAcceptResponse, # Returns acceptance message
          status_code=202, # HTTP 202 Accepted status code
          summary="Run ABM Pipeline Asynchronously",
          tags=["Processing"])
async def run_pipeline_api(
    contact: ContactInput,
    background_tasks: BackgroundTasks,
    use_crew: bool = False # Add query parameter to optionally enable CrewAI
):
    """
    Accepts contact data and triggers the full ABM pipeline (enrich, evaluate, sync, AI)
    to run in the background. Returns immediately with an 'accepted' status.
    Check server logs for pipeline progress and results for the given contact email.
    """
    logger.info(f"Received pipeline request for: {contact.email} (Use CrewAI: {use_crew})")
    # Use model_dump() for Pydantic v2+
    contact_dict = contact.model_dump()
    logger.debug(f"Queuing background task for run_abm_pipeline with data: {contact_dict}")

    # Add the potentially long-running task to FastAPI's background runner
    # The run_abm_pipeline function itself should handle all internal logging
    background_tasks.add_task(
        run_abm_pipeline,
        trigger_contact=contact_dict, # Pass the validated dict
        use_crew=use_crew
    )

    logger.info(f"Background task queued for {contact.email}.")
    # Return the acceptance response immediately
    return PipelineAcceptResponse(
                message="Pipeline task queued for background execution. Check server logs for progress.",
                contact_email=contact.email
           )

# Note: To see the actual results of the background pipeline,
# you would typically:
# 1. Check server logs (as implemented here).
# 2. Have the pipeline write results to a database or cache.
# 3. Implement a separate endpoint to query the status/result by task ID or contact email.
# 4. Use WebSockets for real-time updates (more complex).

@app.on_event("shutdown")
async def shutdown_event():
    """Log on API shutdown."""
    logger.info("--- ABM API Shutting Down ---")