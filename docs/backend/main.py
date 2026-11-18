from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Literal
from urllib.parse import urlencode

from clinical_trials import search_clinical_trials
from drug_search import search_drugs

from database import (
    initialize_db,
    save_search,
    save_references,
    get_search_history,
    get_references,
    update_verification
)


app = FastAPI(
    title="Pharma Reference Finder API",
    description="Search pharmaceutical drugs and clinical trials",
    version="2.0.0"
)


# Frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Initialize database
initialize_db()


class SearchRequest(BaseModel):
    search_type: Literal["drug", "trial"]
    search_value: str


class VerificationRequest(BaseModel):
    status: Literal["pending", "verified", "rejected"]


@app.get("/")
def home():
    return {
        "message": "Pharma Reference Finder Backend is running!",
        "version": "2.0.0"
    }


# Search drugs and clinical trials
@app.post("/search")
def search_references(request: SearchRequest):

    search_value = request.search_value.strip()

    if not search_value:
        raise HTTPException(
            status_code=400,
            detail="Search value cannot be empty"
        )

    search_id = save_search(
        request.search_type,
        search_value
    )

    if request.search_type == "trial":

        results = search_clinical_trials(search_value)
        message = "Clinical trials search completed"

        references = [
            {
                "source_name": "ClinicalTrials.gov",
                "reference_url": item["url"],
                "source_type": "clinical_trial"
            }
            for item in results
            if item.get("url")
        ]

    else:

        results = search_drugs(search_value)
        message = "Drug search completed"

        fda_url = (
            "https://api.fda.gov/drug/label.json?"
            + urlencode({
                "search": search_value,
                "limit": 10
            })
        )

        references = [
            {
                "source_name": "FDA OpenFDA",
                "reference_url": fda_url,
                "source_type": "drug_label"
            }
            for item in results
        ]

    if references:
        save_references(search_id, references)

    return {
        "status": "success",
        "search_id": search_id,
        "search_type": request.search_type,
        "search_value": search_value,
        "message": message,
        "result_count": len(results),
        "results": results
    }


# Display previous searches
@app.get("/history")
def search_history():

    history = get_search_history()

    return {
        "status": "success",
        "total": len(history),
        "history": history
    }


# Retrieve references for a search
@app.get("/references/{search_id}")
def reference_list(search_id: int):

    references = get_references(search_id)

    return {
        "status": "success",
        "search_id": search_id,
        "total": len(references),
        "references": references
    }


# Update reference verification status
@app.patch("/references/{reference_id}/verification")
def verify_reference(
    reference_id: int,
    request: VerificationRequest
):

    updated = update_verification(
        reference_id,
        request.status
    )

    if not updated:
        raise HTTPException(
            status_code=404,
            detail="Reference not found"
        )

    return {
        "status": "success",
        "reference_id": reference_id,
        "verification_status": request.status,
        "message": "Reference status updated"
    }
