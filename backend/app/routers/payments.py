from __future__ import annotations

from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from app.schemas import PaymentRecord

router = APIRouter(prefix="/api/payments", tags=["payments"])


@router.get("/{npi}", response_model=list[PaymentRecord])
def get_payments(npi: str, db: Session = Depends(get_db)) -> list[PaymentRecord]:
    payments = (
        db.query(models.Payment)
        .filter_by(investigator_npi=npi)
        .order_by(models.Payment.year.desc(), models.Payment.amount_usd.desc())
        .all()
    )
    return [PaymentRecord.model_validate(p) for p in payments]


@router.get("", response_model=list[PaymentRecord])
def list_all_payments(
    year: Optional[int] = Query(None),
    company: Optional[str] = Query(None),
    nature: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
) -> list[PaymentRecord]:
    query = db.query(models.Payment)
    if year:
        query = query.filter(models.Payment.year == year)
    if company:
        query = query.filter(models.Payment.company_name.ilike(f"%{company}%"))
    if nature:
        query = query.filter(models.Payment.nature_of_payment.ilike(f"%{nature}%"))

    payments = (
        query.order_by(models.Payment.amount_usd.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return [PaymentRecord.model_validate(p) for p in payments]
