from __future__ import annotations

from datetime import date
from typing import Optional
from pydantic import BaseModel, ConfigDict


class InstitutionSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    type: Optional[str]
    city: Optional[str]
    state: Optional[str]
    lat: Optional[float]
    lon: Optional[float]
    trial_count: int
    kol_count: int
    disease_burden_rate: Optional[float]


class KOLSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    npi: str
    name: str
    specialty: Optional[str]
    state: Optional[str]
    city: Optional[str]
    institution_name: Optional[str] = None
    kol_score: float
    trial_score: float
    pub_score: float
    activity_score: float
    geographic_reach_score: float
    payment_total_usd: float
    payment_company_count: int


class TrialRef(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    nct_id: str
    title: Optional[str]
    phase: Optional[str]
    status: Optional[str]
    sponsor: Optional[str]
    start_date: Optional[date]
    role: Optional[str]


class PublicationRef(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    pmid: str
    title: Optional[str]
    journal: Optional[str]
    year: Optional[int]
    citation_count: int
    author_order: Optional[int]


class PaymentRecord(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company_name: Optional[str]
    amount_usd: float
    nature_of_payment: Optional[str]
    year: Optional[int]
    record_id: Optional[str]


class KOLDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    npi: str
    name: str
    specialty: Optional[str]
    state: Optional[str]
    city: Optional[str]
    institution: Optional[InstitutionSummary]
    kol_score: float
    trial_score: float
    pub_score: float
    activity_score: float
    geographic_reach: int
    geographic_reach_score: float
    payment_total_usd: float
    payment_company_count: int
    trials: list[TrialRef] = []
    publications: list[PublicationRef] = []
    payments: list[PaymentRecord] = []


class GraphNode(BaseModel):
    id: str
    label: str
    type: str
    score: float
    state: Optional[str]
    institution: Optional[str]


class GraphLink(BaseModel):
    source: str
    target: str
    type: str


class GraphResponse(BaseModel):
    nodes: list[GraphNode]
    links: list[GraphLink]


class KOLListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[KOLSummary]


class DiseaseBurdenRecord(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    state: str
    cancer_type: str
    year: int
    incidence_rate: Optional[float]
    mortality_rate: Optional[float]


class ExplanationResponse(BaseModel):
    npi: str
    rationale: str
    engagement_type: str
    compliance_note: str
    cached: bool = False
