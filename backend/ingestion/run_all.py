from __future__ import annotations

"""
Orchestrator: runs all ingestion scripts in order, then computes scores.
Usage:
    python ingestion/run_all.py           # full ingestion
    python ingestion/run_all.py --dry-run # validate without writing
    python ingestion/run_all.py --skip-pubmed  # skip slow PubMed step
"""
import asyncio
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import SessionLocal
from app.services.scoring import compute_all_scores
import ingestion.clinicaltrials as ct
import ingestion.pubmed as pm
import ingestion.cms_payments as cms
import ingestion.seer as seer_loader


def print_header(title: str) -> None:
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")


async def main() -> None:
    dry_run = "--dry-run" in sys.argv
    skip_pubmed = "--skip-pubmed" in sys.argv

    if dry_run:
        print("🔍 DRY RUN MODE — no data will be written\n")

    t0 = time.time()

    print_header("Step 1/4: ClinicalTrials.gov")
    await ct.run(dry_run=dry_run)

    if not skip_pubmed:
        print_header("Step 2/4: PubMed Publications")
        await pm.run(dry_run=dry_run)
    else:
        print_header("Step 2/4: PubMed [SKIPPED]")

    print_header("Step 3/4: CMS Open Payments")
    await cms.run(dry_run=dry_run)

    print_header("Step 4/4: SEER Disease Burden")
    seer_loader.run(dry_run=dry_run)

    if not dry_run:
        print_header("Computing Scores")
        db = SessionLocal()
        try:
            compute_all_scores(db)
        finally:
            db.close()

    elapsed = time.time() - t0
    print(f"\n{'=' * 60}")
    print(f"  Ingestion complete in {elapsed:.1f}s")
    print(f"{'=' * 60}")

    if not dry_run:
        # Print summary
        db = SessionLocal()
        try:
            from app import models
            inv_count = db.query(models.Investigator).count()
            trial_count = db.query(models.Trial).count()
            pub_count = db.query(models.Publication).count()
            payment_count = db.query(models.Payment).count()
            inst_count = db.query(models.Institution).count()
            print(f"\nDatabase summary:")
            print(f"  Investigators : {inv_count}")
            print(f"  Institutions  : {inst_count}")
            print(f"  Trials        : {trial_count}")
            print(f"  Publications  : {pub_count}")
            print(f"  Payments      : {payment_count}")
        finally:
            db.close()


if __name__ == "__main__":
    asyncio.run(main())
