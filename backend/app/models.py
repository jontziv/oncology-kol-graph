from __future__ import annotations

from datetime import date
from typing import Optional
from sqlalchemy import Integer, String, Float, Date, ForeignKey, Text
from sqlalchemy.orm import relationship, mapped_column, Mapped
from app.database import Base


class Institution(Base):
    __tablename__ = "institutions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    type: Mapped[Optional[str]] = mapped_column(String)
    city: Mapped[Optional[str]] = mapped_column(String)
    state: Mapped[Optional[str]] = mapped_column(String, index=True)
    lat: Mapped[Optional[float]] = mapped_column(Float)
    lon: Mapped[Optional[float]] = mapped_column(Float)
    trial_count: Mapped[int] = mapped_column(Integer, default=0)
    kol_count: Mapped[int] = mapped_column(Integer, default=0)
    disease_burden_rate: Mapped[Optional[float]] = mapped_column(Float)

    investigators: Mapped[list[Investigator]] = relationship(back_populates="institution")


class Investigator(Base):
    __tablename__ = "investigators"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    npi: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    specialty: Mapped[Optional[str]] = mapped_column(String)
    institution_id: Mapped[Optional[int]] = mapped_column(ForeignKey("institutions.id"))
    state: Mapped[Optional[str]] = mapped_column(String, index=True)
    city: Mapped[Optional[str]] = mapped_column(String)
    npi_source: Mapped[str] = mapped_column(String, default="clinicaltrials_derived")

    kol_score: Mapped[float] = mapped_column(Float, default=0.0)
    trial_score: Mapped[float] = mapped_column(Float, default=0.0)
    pub_score: Mapped[float] = mapped_column(Float, default=0.0)
    activity_score: Mapped[float] = mapped_column(Float, default=0.0)
    geographic_reach: Mapped[int] = mapped_column(Integer, default=0)
    geographic_reach_score: Mapped[float] = mapped_column(Float, default=0.0)
    payment_total_usd: Mapped[float] = mapped_column(Float, default=0.0)
    payment_company_count: Mapped[int] = mapped_column(Integer, default=0)

    institution: Mapped[Optional[Institution]] = relationship(back_populates="investigators")
    trial_links: Mapped[list[TrialInvestigator]] = relationship(back_populates="investigator")
    publication_links: Mapped[list[PublicationAuthor]] = relationship(back_populates="investigator")
    payments: Mapped[list[Payment]] = relationship(back_populates="investigator")
    explanation: Mapped[Optional[KOLExplanation]] = relationship(back_populates="investigator", uselist=False)


class Trial(Base):
    __tablename__ = "trials"

    nct_id: Mapped[str] = mapped_column(String, primary_key=True)
    title: Mapped[Optional[str]] = mapped_column(Text)
    phase: Mapped[Optional[str]] = mapped_column(String)
    status: Mapped[Optional[str]] = mapped_column(String, index=True)
    condition: Mapped[Optional[str]] = mapped_column(Text)
    sponsor: Mapped[Optional[str]] = mapped_column(String)
    start_date: Mapped[Optional[date]] = mapped_column(Date)
    completion_date: Mapped[Optional[date]] = mapped_column(Date)
    enrollment: Mapped[Optional[int]] = mapped_column(Integer)

    investigator_links: Mapped[list[TrialInvestigator]] = relationship(back_populates="trial")


class TrialInvestigator(Base):
    __tablename__ = "trial_investigators"

    trial_nct_id: Mapped[str] = mapped_column(ForeignKey("trials.nct_id"), primary_key=True)
    investigator_npi: Mapped[str] = mapped_column(ForeignKey("investigators.npi"), primary_key=True)
    role: Mapped[Optional[str]] = mapped_column(String)

    trial: Mapped[Trial] = relationship(back_populates="investigator_links")
    investigator: Mapped[Investigator] = relationship(back_populates="trial_links")


class Publication(Base):
    __tablename__ = "publications"

    pmid: Mapped[str] = mapped_column(String, primary_key=True)
    title: Mapped[Optional[str]] = mapped_column(Text)
    journal: Mapped[Optional[str]] = mapped_column(String)
    year: Mapped[Optional[int]] = mapped_column(Integer, index=True)
    citation_count: Mapped[int] = mapped_column(Integer, default=0)
    abstract: Mapped[Optional[str]] = mapped_column(Text)

    author_links: Mapped[list[PublicationAuthor]] = relationship(back_populates="publication")


class PublicationAuthor(Base):
    __tablename__ = "publication_authors"

    pmid: Mapped[str] = mapped_column(ForeignKey("publications.pmid"), primary_key=True)
    investigator_npi: Mapped[str] = mapped_column(ForeignKey("investigators.npi"), primary_key=True)
    author_order: Mapped[Optional[int]] = mapped_column(Integer)

    publication: Mapped[Publication] = relationship(back_populates="author_links")
    investigator: Mapped[Investigator] = relationship(back_populates="publication_links")


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    investigator_npi: Mapped[str] = mapped_column(ForeignKey("investigators.npi"), index=True)
    company_name: Mapped[Optional[str]] = mapped_column(String)
    amount_usd: Mapped[float] = mapped_column(Float, default=0.0)
    nature_of_payment: Mapped[Optional[str]] = mapped_column(String)
    year: Mapped[Optional[int]] = mapped_column(Integer)
    record_id: Mapped[Optional[str]] = mapped_column(String, unique=True)

    investigator: Mapped[Investigator] = relationship(back_populates="payments")


class SEERStateData(Base):
    __tablename__ = "seer_state_data"

    state: Mapped[str] = mapped_column(String, primary_key=True)
    cancer_type: Mapped[str] = mapped_column(String, primary_key=True, default="Lung and Bronchus")
    year: Mapped[int] = mapped_column(Integer, primary_key=True, default=2021)
    incidence_rate: Mapped[Optional[float]] = mapped_column(Float)
    mortality_rate: Mapped[Optional[float]] = mapped_column(Float)


class KOLExplanation(Base):
    __tablename__ = "kol_explanations"

    npi: Mapped[str] = mapped_column(ForeignKey("investigators.npi"), primary_key=True)
    rationale: Mapped[Optional[str]] = mapped_column(Text)
    engagement_type: Mapped[Optional[str]] = mapped_column(String)
    compliance_note: Mapped[Optional[str]] = mapped_column(Text)
    generated_at: Mapped[Optional[date]] = mapped_column(Date)

    investigator: Mapped[Investigator] = relationship(back_populates="explanation")
