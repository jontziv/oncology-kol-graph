from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import text
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db

router = APIRouter(prefix="/api/engagements", tags=["engagements"])


def get_user_id(request: Request) -> str:
    """Extract user_id from Supabase auth token in Authorization header"""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")

    token = auth_header[7:]  # Remove "Bearer " prefix

    # For MVP: use the token as-is, frontend sends user_id in X-User-ID header
    # In production, you'd verify the JWT signature here
    user_id = request.headers.get("X-User-ID", "")
    if not user_id:
        raise HTTPException(status_code=401, detail="Missing X-User-ID header")

    return user_id


class EngagementUpdate(BaseModel):
    npi: str
    status: str = "To Engage"
    notes: str = ""
    assigned_to: str = ""


class EngagementResponse(BaseModel):
    id: str
    npi: str
    status: str
    notes: str
    assigned_to: str
    created_at: str
    updated_at: str


@router.get("/{npi}", response_model=EngagementResponse | None)
def get_engagement(npi: str, db: Session = Depends(get_db), user_id: str = Depends(get_user_id)):
    """Get engagement record for current user + KOL"""
    result = db.execute(
        text("""
            SELECT id, npi, status, notes, assigned_to, created_at, updated_at
            FROM kol_engagements
            WHERE user_id = :user_id AND npi = :npi
        """),
        {"user_id": user_id, "npi": npi}
    ).first()

    if not result:
        return None

    return EngagementResponse(
        id=result[0],
        npi=result[1],
        status=result[2],
        notes=result[3],
        assigned_to=result[4],
        created_at=str(result[5]),
        updated_at=str(result[6]),
    )


@router.post("", response_model=EngagementResponse)
def save_engagement(data: EngagementUpdate, db: Session = Depends(get_db), user_id: str = Depends(get_user_id)):
    """Create or update engagement record"""
    # Try update first
    result = db.execute(
        text("""
            UPDATE kol_engagements
            SET status = :status, notes = :notes, assigned_to = :assigned_to, updated_at = NOW()
            WHERE user_id = :user_id AND npi = :npi
            RETURNING id, npi, status, notes, assigned_to, created_at, updated_at
        """),
        {"user_id": user_id, "npi": data.npi, "status": data.status, "notes": data.notes, "assigned_to": data.assigned_to}
    ).first()

    # If no rows updated, insert
    if not result:
        result = db.execute(
            text("""
                INSERT INTO kol_engagements (user_id, npi, status, notes, assigned_to)
                VALUES (:user_id, :npi, :status, :notes, :assigned_to)
                RETURNING id, npi, status, notes, assigned_to, created_at, updated_at
            """),
            {"user_id": user_id, "npi": data.npi, "status": data.status, "notes": data.notes, "assigned_to": data.assigned_to}
        ).first()

    db.commit()

    return EngagementResponse(
        id=result[0],
        npi=result[1],
        status=result[2],
        notes=result[3],
        assigned_to=result[4],
        created_at=str(result[5]),
        updated_at=str(result[6]),
    )
