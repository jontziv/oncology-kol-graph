from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from app.schemas import DiseaseBurdenRecord

router = APIRouter(prefix="/api/disease-burden", tags=["disease-burden"])


@router.get("", response_model=list[DiseaseBurdenRecord])
def get_disease_burden(db: Session = Depends(get_db)) -> list[DiseaseBurdenRecord]:
    records = (
        db.query(models.SEERStateData)
        .filter_by(cancer_type="Lung and Bronchus")
        .order_by(models.SEERStateData.incidence_rate.desc())
        .all()
    )
    return [DiseaseBurdenRecord.model_validate(r) for r in records]
