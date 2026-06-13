from __future__ import annotations

from typing import Literal, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app import models
from app.schemas import KOLListResponse, KOLSummary, KOLDetail, TrialRef, PublicationRef, PaymentRecord

router = APIRouter(prefix="/api/kols", tags=["kols"])

SORTABLE_FIELDS = {
    "kol_score": models.Investigator.kol_score,
    "trial_score": models.Investigator.trial_score,
    "pub_score": models.Investigator.pub_score,
    "activity_score": models.Investigator.activity_score,
    "payment_total_usd": models.Investigator.payment_total_usd,
    "name": models.Investigator.name,
}


def _to_kol_summary(inv: models.Investigator) -> KOLSummary:
    return KOLSummary(
        npi=inv.npi,
        name=inv.name,
        specialty=inv.specialty,
        state=inv.state,
        city=inv.city,
        institution_name=inv.institution.name if inv.institution else None,
        kol_score=inv.kol_score,
        trial_score=inv.trial_score,
        pub_score=inv.pub_score,
        activity_score=inv.activity_score,
        geographic_reach_score=inv.geographic_reach_score,
        payment_total_usd=inv.payment_total_usd,
        payment_company_count=inv.payment_company_count,
    )


@router.get("", response_model=KOLListResponse)
def list_kols(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = Query("kol_score"),
    order: Literal["asc", "desc"] = Query("desc"),
    state: Optional[str] = Query(None),
    min_score: float = Query(0.0, ge=0, le=100),
    db: Session = Depends(get_db),
) -> KOLListResponse:
    sort_col = SORTABLE_FIELDS.get(sort_by, models.Investigator.kol_score)
    sort_expr = sort_col.asc() if order == "asc" else sort_col.desc()

    query = db.query(models.Investigator).options(joinedload(models.Investigator.institution))
    if state:
        query = query.filter(models.Investigator.state == state)
    if min_score > 0:
        query = query.filter(models.Investigator.kol_score >= min_score)

    total = query.count()
    investigators = query.order_by(sort_expr).offset((page - 1) * page_size).limit(page_size).all()

    return KOLListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[_to_kol_summary(inv) for inv in investigators],
    )


@router.get("/{npi}", response_model=KOLDetail)
def get_kol(npi: str, db: Session = Depends(get_db)) -> KOLDetail:
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

    from app.schemas import InstitutionSummary
    inst_schema = None
    if inv.institution:
        inst_schema = InstitutionSummary.model_validate(inv.institution)

    trials = [
        TrialRef(
            nct_id=link.trial.nct_id,
            title=link.trial.title,
            phase=link.trial.phase,
            status=link.trial.status,
            sponsor=link.trial.sponsor,
            start_date=link.trial.start_date,
            role=link.role,
        )
        for link in inv.trial_links
        if link.trial
    ]

    publications = [
        PublicationRef(
            pmid=link.publication.pmid,
            title=link.publication.title,
            journal=link.publication.journal,
            year=link.publication.year,
            citation_count=link.publication.citation_count,
            author_order=link.author_order,
        )
        for link in inv.publication_links
        if link.publication
    ]

    payments = [
        PaymentRecord(
            id=p.id,
            company_name=p.company_name,
            amount_usd=p.amount_usd,
            nature_of_payment=p.nature_of_payment,
            year=p.year,
            record_id=p.record_id,
        )
        for p in inv.payments
    ]

    return KOLDetail(
        npi=inv.npi,
        name=inv.name,
        specialty=inv.specialty,
        state=inv.state,
        city=inv.city,
        institution=inst_schema,
        kol_score=inv.kol_score,
        trial_score=inv.trial_score,
        pub_score=inv.pub_score,
        activity_score=inv.activity_score,
        geographic_reach=inv.geographic_reach,
        geographic_reach_score=inv.geographic_reach_score,
        payment_total_usd=inv.payment_total_usd,
        payment_company_count=inv.payment_company_count,
        trials=trials,
        publications=publications,
        payments=payments,
    )
