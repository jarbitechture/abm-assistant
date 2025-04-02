# abm/__init__.py

# This marks the abm directory as a Python package.
# No logic required here for now.


# abm/abm_api.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from abm.run_abm_pipeline import run_abm_pipeline
import asyncio

app = FastAPI()

class ContactInput(BaseModel):
    name: str
    email: str
    company: str
    domain: str
    title: str
    phone: str


@app.post("/run-pipeline")
async def run_pipeline_api(contact: ContactInput):
    try:
        enriched_contact = contact.dict()
        result = run_abm_pipeline(trigger_contact=enriched_contact)

        # Optionally extract source metadata and include in API response
        enriched = enrich_contact_data(enriched_contact)
        sources = enriched.get("sources", {})

        return {
            "status": "success",
            "data": result,
            "sources": sources
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.post("/enrich")
async def enrich(contact: ContactInput):
    enriched = enrich_contact_data(contact.dict())
    return {"contact": enriched, "sources": enriched["sources"]}


