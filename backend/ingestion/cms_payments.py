from __future__ import annotations

"""
Pull oncology-related payments from CMS Open Payments API (SODA).
Matches against investigators already in the DB by NPI (for real NPI rows)
or skips provisional NPI rows that start with 'PROV-'.
"""
import asyncio
import sys
import os

import httpx
from sqlalchemy.orm import Session

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app.database import SessionLocal, engine
from app import models

# CMS Open Payments general payments dataset — uses Socrata Open Data API
CMS_API = "https://openpaymentsdata.cms.gov/api/1/datastore/sql"

# Dataset UUIDs for general payments by year (update if CMS rotates IDs)
# These can be found at https://openpaymentsdata.cms.gov/dataset/
DATASET_YEARS = {
    2023: "06731e8c-e3b7-4960-a496-53a05c5f3967",
    2022: "b1e4f1cb-b82a-4ef8-849e-1c2d28fcb5a7",
}

SPECIALTY_FILTER = "oncology"
BATCH_LIMIT = 500


async def fetch_payments_for_npis(
    client: httpx.AsyncClient,
    npis: list[str],
    year: int,
    dataset_id: str,
) -> list[dict]:
    """Query CMS SODA API for payments to a batch of real NPIs."""
    npi_list = ", ".join(f"'{n}'" for n in npis)
    query = (
        f"SELECT covered_recipient_npi, "
        f"applicable_manufacturer_or_applicable_gpo_making_payment_name, "
        f"total_amount_of_payment_usdollars, "
        f"nature_of_payment_or_transfer_of_value, "
        f"program_year, record_id "
        f"FROM {dataset_id} "
        f"WHERE covered_recipient_npi IN ({npi_list}) "
        f"LIMIT {BATCH_LIMIT}"
    )
    resp = await client.get(
        CMS_API,
        params={"query": query},
        timeout=30,
    )
    if resp.status_code != 200:
        return []
    return resp.json()


async def fetch_payments_by_specialty(
    client: httpx.AsyncClient,
    year: int,
    dataset_id: str,
) -> list[dict]:
    """Fallback: pull oncology payments broadly when no real NPIs available."""
    query = (
        f"SELECT covered_recipient_npi, covered_recipient_last_name, "
        f"covered_recipient_first_name, "
        f"applicable_manufacturer_or_applicable_gpo_making_payment_name, "
        f"total_amount_of_payment_usdollars, "
        f"nature_of_payment_or_transfer_of_value, "
        f"program_year, record_id "
        f"FROM {dataset_id} "
        f"WHERE LOWER(covered_recipient_specialty_1) LIKE '%oncology%' "
        f"LIMIT {BATCH_LIMIT}"
    )
    resp = await client.get(CMS_API, params={"query": query}, timeout=30)
    if resp.status_code != 200:
        print(f"  CMS API returned {resp.status_code}: {resp.text[:200]}")
        return []
    return resp.json()


def upsert_payment(db: Session, row: dict, npi: str) -> None:
    record_id = str(row.get("record_id", "")).strip() or None
    if record_id:
        existing = db.query(models.Payment).filter_by(record_id=record_id).first()
        if existing:
            return

    try:
        amount = float(row.get("total_amount_of_payment_usdollars") or 0)
    except (ValueError, TypeError):
        amount = 0.0

    year_val = None
    try:
        year_val = int(row.get("program_year") or 0) or None
    except (ValueError, TypeError):
        pass

    db.add(models.Payment(
        investigator_npi=npi,
        company_name=row.get("applicable_manufacturer_or_applicable_gpo_making_payment_name"),
        amount_usd=amount,
        nature_of_payment=row.get("nature_of_payment_or_transfer_of_value"),
        year=year_val,
        record_id=record_id,
    ))


async def run(dry_run: bool = False) -> None:
    models.Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Get real NPIs (non-provisional) from DB
    real_npis = [
        row[0] for row in
        db.query(models.Investigator.npi)
        .filter(~models.Investigator.npi.startswith("PROV-"))
        .all()
    ]

    print(f"Found {len(real_npis)} real NPIs in DB")

    async with httpx.AsyncClient() as client:
        total_payments = 0

        for year, dataset_id in DATASET_YEARS.items():
            print(f"\nFetching CMS Open Payments {year}...")

            if real_npis:
                # Process in batches of 50 NPIs
                for i in range(0, len(real_npis), 50):
                    batch = real_npis[i:i + 50]
                    rows = await fetch_payments_for_npis(client, batch, year, dataset_id)
                    for row in rows:
                        npi = str(row.get("covered_recipient_npi", "")).strip()
                        if npi and npi in real_npis:
                            if not dry_run:
                                upsert_payment(db, row, npi)
                    total_payments += len(rows)
                    await asyncio.sleep(0.3)
            else:
                # Fallback: specialty-based search, match names to provisional investigators
                rows = await fetch_payments_by_specialty(client, year, dataset_id)
                print(f"  Specialty fallback: {len(rows)} oncology payment records")

                inv_index = {
                    inv.name.lower(): inv.npi
                    for inv in db.query(models.Investigator).all()
                }

                for row in rows:
                    last = str(row.get("covered_recipient_last_name", "")).strip().lower()
                    first = str(row.get("covered_recipient_first_name", "")).strip().lower()
                    full = f"{first} {last}".strip()

                    matched_npi = inv_index.get(full) or inv_index.get(f"{last}, {first}")
                    if matched_npi and not dry_run:
                        upsert_payment(db, row, matched_npi)
                    total_payments += 1

            if not dry_run:
                db.commit()

    if dry_run:
        db.rollback()
        print(f"\n[dry-run] Would process ~{total_payments} payment records. No data written.")
    else:
        payment_count = db.query(models.Payment).count()
        print(f"\n✓ CMS Open Payments ingestion complete: {payment_count} records stored")

    db.close()


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    asyncio.run(run(dry_run=dry_run))
