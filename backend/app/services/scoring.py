from __future__ import annotations

"""
Deterministic KOL and institution scoring.
All functions are pure: they take DB rows, return updated values.
Run as a post-ingestion step via run_all.py or directly.
"""
import math
import sys
import os
from datetime import date, timedelta
from typing import Optional

from sqlalchemy.orm import Session

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from app import models

THREE_YEARS_AGO = date.today() - timedelta(days=3 * 365)

PHASE_WEIGHTS = {
    "Phase 3": 3.0, "Phase 2": 2.0, "Phase 1": 1.0,
    "Early Phase 1": 0.75, "Phase 4": 2.5, "N/A": 0.5,
}
STATUS_WEIGHTS = {
    "Recruiting": 1.5, "Active, not recruiting": 1.0,
    "Completed": 0.7, "Terminated": 0.3, "Withdrawn": 0.1,
    "Not yet recruiting": 1.2, "Enrolling by invitation": 1.1,
}


def _phase_weight(phase: Optional[str]) -> float:
    if not phase:
        return 0.5
    for key, w in PHASE_WEIGHTS.items():
        if key.lower() in (phase or "").lower():
            return w
    return 0.5


def _status_weight(status: Optional[str]) -> float:
    if not status:
        return 0.5
    for key, w in STATUS_WEIGHTS.items():
        if key.lower() in (status or "").lower():
            return w
    return 0.5


def compute_raw_trial_score(trial_links: list[models.TrialInvestigator]) -> float:
    raw = 0.0
    for link in trial_links:
        trial = link.trial
        if trial is None:
            continue
        raw += _phase_weight(trial.phase) * _status_weight(trial.status)
    return raw


def compute_raw_pub_score(pub_links: list[models.PublicationAuthor]) -> float:
    raw = 0.0
    for link in pub_links:
        pub = link.publication
        if pub is None:
            continue
        raw += math.log1p(pub.citation_count or 0)
    return raw


def compute_raw_activity_score(trial_links: list[models.TrialInvestigator]) -> float:
    raw = 0.0
    for link in trial_links:
        trial = link.trial
        if trial is None:
            continue
        weight = 2.0 if (trial.start_date and trial.start_date >= THREE_YEARS_AGO) else 1.0
        raw += weight
    return raw


def compute_geographic_reach(trial_links: list[models.TrialInvestigator], db: Session) -> int:
    """Count distinct states across all trials the investigator is on."""
    nct_ids = [link.trial_nct_id for link in trial_links]
    if not nct_ids:
        return 0
    # Get all investigators on the same trials to count distinct states
    inv_npis = (
        db.query(models.TrialInvestigator.investigator_npi)
        .filter(models.TrialInvestigator.trial_nct_id.in_(nct_ids))
        .subquery()
    )
    states = (
        db.query(models.Investigator.state)
        .filter(models.Investigator.npi.in_(inv_npis))
        .filter(models.Investigator.state.isnot(None))
        .distinct()
        .all()
    )
    return len(states)


def normalize(value: float, max_value: float) -> float:
    if max_value <= 0:
        return 0.0
    return min(value / max_value * 100.0, 100.0)


def compute_all_scores(db: Session) -> None:
    """Compute and persist scores for all investigators. Idempotent."""
    print("Loading investigators...")
    investigators = (
        db.query(models.Investigator)
        .all()
    )

    if not investigators:
        print("No investigators found.")
        return

    print(f"  Computing raw scores for {len(investigators)} investigators...")

    # Pass 1: compute raw scores
    raw_data: dict[str, dict] = {}
    for inv in investigators:
        trial_links = inv.trial_links
        pub_links = inv.publication_links

        raw_trial = compute_raw_trial_score(trial_links)
        raw_pub = compute_raw_pub_score(pub_links)
        raw_activity = compute_raw_activity_score(trial_links)
        geo_reach = compute_geographic_reach(trial_links, db)

        raw_data[inv.npi] = {
            "raw_trial": raw_trial,
            "raw_pub": raw_pub,
            "raw_activity": raw_activity,
            "geo_reach": geo_reach,
        }

    # Pass 2: find maxima for normalization
    max_trial = max((d["raw_trial"] for d in raw_data.values()), default=1.0) or 1.0
    max_pub = max((d["raw_pub"] for d in raw_data.values()), default=1.0) or 1.0
    max_activity = max((d["raw_activity"] for d in raw_data.values()), default=1.0) or 1.0
    max_geo = 10  # cap at 10 states for geographic reach score

    # Pass 3: normalise and compute composite
    for inv in investigators:
        d = raw_data[inv.npi]

        trial_score = normalize(d["raw_trial"], max_trial)
        pub_score = normalize(d["raw_pub"], max_pub)
        activity_score = normalize(d["raw_activity"], max_activity)
        geo_score = min(d["geo_reach"] / max_geo * 100.0, 100.0)

        kol_score = (
            0.35 * trial_score
            + 0.30 * pub_score
            + 0.20 * activity_score
            + 0.15 * geo_score
        )

        # Payment aggregates
        payment_total = sum(p.amount_usd for p in inv.payments)
        payment_companies = len({p.company_name for p in inv.payments if p.company_name})

        inv.trial_score = round(trial_score, 2)
        inv.pub_score = round(pub_score, 2)
        inv.activity_score = round(activity_score, 2)
        inv.geographic_reach = d["geo_reach"]
        inv.geographic_reach_score = round(geo_score, 2)
        inv.kol_score = round(kol_score, 2)
        inv.payment_total_usd = round(payment_total, 2)
        inv.payment_company_count = payment_companies

    # Pass 4: update institution aggregates
    _update_institution_aggregates(db)

    db.commit()
    print("✓ Scoring complete")


def _update_institution_aggregates(db: Session) -> None:
    institutions = db.query(models.Institution).all()
    for inst in institutions:
        inst.kol_count = len(inst.investigators)
        # trial_count: distinct trials across all investigators in this institution
        nct_ids: set[str] = set()
        for inv in inst.investigators:
            for link in inv.trial_links:
                nct_ids.add(link.trial_nct_id)
        inst.trial_count = len(nct_ids)

        # disease burden: look up SEER for this state
        if inst.state:
            seer = db.get(models.SEERStateData, (inst.state, "Lung and Bronchus", 2021))
            if seer:
                inst.disease_burden_rate = seer.incidence_rate
