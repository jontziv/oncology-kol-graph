from __future__ import annotations

from typing import Literal, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from app.schemas import InstitutionSummary

router = APIRouter(prefix="/api/institutions", tags=["institutions"])

SORTABLE = {
    "trial_count": models.Institution.trial_count,
    "kol_count": models.Institution.kol_count,
    "disease_burden_rate": models.Institution.disease_burden_rate,
    "name": models.Institution.name,
}


@router.get("", response_model=list[InstitutionSummary])
def list_institutions(
    sort_by: str = Query("trial_count"),
    order: Literal["asc", "desc"] = Query("desc"),
    state: Optional[str] = Query(None),
    db: Session = Depends(get_db),
) -> list[InstitutionSummary]:
    sort_col = SORTABLE.get(sort_by, models.Institution.trial_count)
    sort_expr = sort_col.asc() if order == "asc" else sort_col.desc()

    query = db.query(models.Institution)
    if state:
        query = query.filter(models.Institution.state == state)

    institutions = query.order_by(sort_expr).limit(200).all()
    return [InstitutionSummary.model_validate(inst) for inst in institutions]
