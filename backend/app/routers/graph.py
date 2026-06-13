from __future__ import annotations

from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import GraphResponse
from app.services.graph_builder import build_full_graph, build_egocentric_network

router = APIRouter(prefix="/api/graph", tags=["graph"])


@router.get("", response_model=GraphResponse)
def get_full_graph(
    min_score: float = Query(0.0, ge=0, le=100),
    state: Optional[str] = Query(None),
    db: Session = Depends(get_db),
) -> GraphResponse:
    return build_full_graph(db, min_score=min_score, state=state)


@router.get("/network/{npi}", response_model=GraphResponse)
def get_kol_network(npi: str, db: Session = Depends(get_db)) -> GraphResponse:
    return build_egocentric_network(db, npi=npi)
