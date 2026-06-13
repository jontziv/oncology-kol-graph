from __future__ import annotations

"""
Pull NSCLC trials from ClinicalTrials.gov v2 API.
Upserts: institutions, investigators (provisional NPI), trials, trial_investigators.
Run time: ~2-5 min depending on result count.
"""
import asyncio
import hashlib
import sys
import os
from datetime import date

import httpx
from sqlalchemy.orm import Session
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app.database import SessionLocal, engine
from app import models

BASE_URL = "https://clinicaltrials.gov/api/v2/studies"
PAGE_SIZE = 100
SEARCH_CONDITION = "NSCLC OR \"non-small cell lung cancer\""
SEARCH_LOCATION = "United States"


def _make_provisional_npi(name: str, institution: str) -> str:
    """Deterministic provisional NPI from name + institution hash (no real NPI available)."""
    raw = f"{name.lower().strip()}|{institution.lower().strip()}"
    return "PROV-" + hashlib.sha1(raw.encode()).hexdigest()[:12]


def _parse_date(s: str | None) -> date | None:
    if not s:
        return None
    for fmt in ("%Y-%m-%d", "%Y-%m", "%Y"):
        try:
            from datetime import datetime
            return datetime.strptime(s[:len(fmt)], fmt).date()
        except ValueError:
            continue
    return None


def _extract_phase(phases: list | None) -> str | None:
    if not phases:
        return None
    mapping = {
        "PHASE1": "Phase 1", "PHASE2": "Phase 2",
        "PHASE3": "Phase 3", "PHASE4": "Phase 4",
        "NA": "N/A", "EARLY_PHASE1": "Early Phase 1",
    }
    return mapping.get(phases[0], phases[0])


def _upsert_institution(db: Session, name: str, city: str | None, state: str | None) -> int:
    name = name.strip()
    existing = db.query(models.Institution).filter_by(name=name).first()
    if existing:
        return existing.id
    inst = models.Institution(name=name, city=city, state=state)
    db.add(inst)
    db.flush()
    return inst.id


def _upsert_investigator(
    db: Session, name: str, institution_id: int, city: str | None, state: str | None
) -> str:
    # Institutions table gives us the institution name for NPI generation
    inst = db.get(models.Institution, institution_id)
    inst_name = inst.name if inst else ""
    npi = _make_provisional_npi(name, inst_name)
    existing = db.query(models.Investigator).filter_by(npi=npi).first()
    if not existing:
        inv = models.Investigator(
            npi=npi,
            name=name.strip(),
            institution_id=institution_id,
            city=city,
            state=state,
            npi_source="clinicaltrials_derived",
        )
        db.add(inv)
        db.flush()
    return npi


async def fetch_studies(client: httpx.AsyncClient) -> list[dict]:
    studies = []
    next_token = None
    page = 1

    while True:
        params: dict = {
            "query.cond": SEARCH_CONDITION,
            "query.locn": SEARCH_LOCATION,
            "pageSize": PAGE_SIZE,
            "format": "json",
        }
        if next_token:
            params["pageToken"] = next_token

        resp = await client.get(BASE_URL, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        batch = data.get("studies", [])
        studies.extend(batch)
        print(f"  Page {page}: fetched {len(batch)} studies (total so far: {len(studies)})")

        next_token = data.get("nextPageToken")
        if not next_token or not batch:
            break
        page += 1

    return studies


def process_study(db: Session, study: dict) -> None:
    proto = study.get("protocolSection", {})

    # ── Trial core ───────────────────────────────────────────────────────────
    id_mod = proto.get("identificationModule", {})
    nct_id = id_mod.get("nctId")
    if not nct_id:
        return

    status_mod = proto.get("statusModule", {})
    design_mod = proto.get("designModule", {})
    desc_mod = proto.get("descriptionModule", {})
    sponsor_mod = proto.get("sponsorCollaboratorsModule", {})

    phase_list = design_mod.get("phases", [])
    phase = _extract_phase(phase_list)
    status = status_mod.get("overallStatus")
    enrollment_info = design_mod.get("enrollmentInfo", {})

    existing_trial = db.get(models.Trial, nct_id)
    if existing_trial:
        existing_trial.status = status
    else:
        trial = models.Trial(
            nct_id=nct_id,
            title=id_mod.get("briefTitle"),
            phase=phase,
            status=status,
            condition=", ".join(proto.get("conditionsModule", {}).get("conditions", [])),
            sponsor=sponsor_mod.get("leadSponsor", {}).get("name"),
            start_date=_parse_date(status_mod.get("startDateStruct", {}).get("date")),
            completion_date=_parse_date(
                status_mod.get("primaryCompletionDateStruct", {}).get("date")
            ),
            enrollment=enrollment_info.get("count"),
        )
        db.add(trial)
        db.flush()

    # ── Locations → investigators ────────────────────────────────────────────
    contacts_mod = proto.get("contactsLocationsModule", {})
    locations = contacts_mod.get("locations", [])

    # Track (nct_id, npi) pairs added within this study to avoid intra-batch duplicates
    seen_links: set[tuple[str, str]] = set()

    for loc in locations:
        loc_facility = loc.get("facility", "Unknown Institution")
        loc_city = loc.get("city")
        loc_state = loc.get("state")
        contacts = loc.get("contacts", [])

        for contact in contacts:
            role_raw = contact.get("role", "")
            if role_raw not in ("PRINCIPAL_INVESTIGATOR", "SUB_INVESTIGATOR"):
                continue
            inv_name = contact.get("name", "").strip()
            if not inv_name or len(inv_name) < 3:
                continue

            institution_id = _upsert_institution(db, loc_facility, loc_city, loc_state)
            npi = _upsert_investigator(db, inv_name, institution_id, loc_city, loc_state)

            link_key = (nct_id, npi)
            if link_key in seen_links:
                continue
            seen_links.add(link_key)

            role_label = "Principal Investigator" if role_raw == "PRINCIPAL_INVESTIGATOR" else "Sub-Investigator"
            existing_link = (
                db.query(models.TrialInvestigator)
                .filter_by(trial_nct_id=nct_id, investigator_npi=npi)
                .first()
            )
            if not existing_link:
                db.add(models.TrialInvestigator(
                    trial_nct_id=nct_id,
                    investigator_npi=npi,
                    role=role_label,
                ))


async def run(dry_run: bool = False) -> None:
    models.Base.metadata.create_all(bind=engine)

    print("Fetching NSCLC studies from ClinicalTrials.gov...")
    async with httpx.AsyncClient() as client:
        studies = await fetch_studies(client)

    print(f"\nProcessing {len(studies)} studies...")
    db = SessionLocal()
    try:
        for i, study in enumerate(studies):
            process_study(db, study)
            if (i + 1) % 50 == 0:
                if not dry_run:
                    db.commit()
                print(f"  Processed {i + 1}/{len(studies)}")

        if not dry_run:
            db.commit()
            inv_count = db.query(models.Investigator).count()
            trial_count = db.query(models.Trial).count()
            print(f"\n✓ ClinicalTrials ingestion complete: {trial_count} trials, {inv_count} investigators")
        else:
            db.rollback()
            print("\n[dry-run] No data written.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    asyncio.run(run(dry_run=dry_run))
