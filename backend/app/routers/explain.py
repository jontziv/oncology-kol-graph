from __future__ import annotations

from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app import models
from app.schemas import ExplanationResponse
from app.services.groq_client import generate_rationale

router = APIRouter(prefix="/api/explain", tags=["explain"])

CACHE_DAYS = 7


@router.get("/{npi}", response_model=ExplanationResponse)
def explain_kol(npi: str, refresh: bool = False, db: Session = Depends(get_db)) -> ExplanationResponse:
    inv = (
        db.query(models.Investigator)
        .options(
            joinedload(models.Investigator.institution),
            joinedload(models.Investigator.trial_links).joinedload(models.TrialInvestigator.trial),
            joinedload(models.Investigator.publication_links).joinedload(models.PublicationAuthor.publication),
            joinedload(models.Investigator.payments),
        )
        .filter_by(npi=npi)
        .first()
    )
    if not inv:
        raise HTTPException(status_code=404, detail="Investigator not found")

    # Serve cached explanation if fresh
    existing = db.get(models.KOLExplanation, npi)
    if existing and not refresh:
        age = (date.today() - existing.generated_at).days if existing.generated_at else 999
        if age < CACHE_DAYS:
            return ExplanationResponse(
                npi=npi,
                rationale=existing.rationale or "",
                engagement_type=existing.engagement_type or "",
                compliance_note=existing.compliance_note or "",
                cached=True,
            )

    # Fetch SEER rate for investigator's state
    seer_rate: float | None = None
    if inv.state:
        seer = db.get(models.SEERStateData, (inv.state, "Lung and Bronchus", 2021))
        if seer:
            seer_rate = seer.incidence_rate

    result = generate_rationale(inv, seer_rate, db)

    # Persist to cache
    if existing:
        existing.rationale = result["rationale"]
        existing.engagement_type = result["engagement_type"]
        existing.compliance_note = result["compliance_note"]
        existing.generated_at = date.today()
    else:
        db.add(models.KOLExplanation(
            npi=npi,
            rationale=result["rationale"],
            engagement_type=result["engagement_type"],
            compliance_note=result["compliance_note"],
            generated_at=date.today(),
        ))
    db.commit()

    return ExplanationResponse(
        npi=npi,
        rationale=result["rationale"],
        engagement_type=result["engagement_type"],
        compliance_note=result["compliance_note"],
        cached=False,
    )
