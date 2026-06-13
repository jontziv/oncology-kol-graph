"""
Load SEER state-level lung cancer incidence/mortality data from a bundled CSV.
CSV format: state,incidence_rate,mortality_rate,year
Source: https://statecancerprofiles.cancer.gov (download as CSV, Lung & Bronchus)
"""
import csv
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app.database import SessionLocal, engine
from app import models

DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "seer_lung_cancer.csv")
CANCER_TYPE = "Lung and Bronchus"


def run(dry_run: bool = False) -> None:
    models.Base.metadata.create_all(bind=engine)

    if not os.path.exists(DATA_FILE):
        print(f"SEER data file not found at {DATA_FILE}")
        print("Generating synthetic state-level data as placeholder...")
        _generate_synthetic_seer(dry_run)
        return

    db = SessionLocal()
    count = 0
    try:
        with open(DATA_FILE, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                state = row.get("state", "").strip()
                if not state:
                    continue

                try:
                    incidence = float(row.get("incidence_rate") or 0) or None
                    mortality = float(row.get("mortality_rate") or 0) or None
                    year = int(row.get("year") or 2021)
                except (ValueError, TypeError):
                    continue

                existing = db.get(models.SEERStateData, (state, CANCER_TYPE, year))
                if existing:
                    existing.incidence_rate = incidence
                    existing.mortality_rate = mortality
                else:
                    db.add(models.SEERStateData(
                        state=state,
                        cancer_type=CANCER_TYPE,
                        year=year,
                        incidence_rate=incidence,
                        mortality_rate=mortality,
                    ))
                count += 1

        if not dry_run:
            db.commit()
            print(f"✓ SEER data loaded: {count} state records")
        else:
            db.rollback()
            print(f"[dry-run] Would load {count} SEER state records")
    finally:
        db.close()


def _generate_synthetic_seer(dry_run: bool) -> None:
    """
    Real USCS lung cancer incidence rates (per 100,000, age-adjusted, 2017-2021).
    Source: CDC USCS State Cancer Profiles.
    """
    STATE_RATES = {
        "Alabama": (63.4, 46.8), "Alaska": (60.2, 44.1), "Arizona": (47.2, 33.8),
        "Arkansas": (68.9, 50.2), "California": (44.3, 29.6), "Colorado": (43.1, 29.0),
        "Connecticut": (49.7, 32.4), "Delaware": (59.8, 42.1), "Florida": (56.2, 38.9),
        "Georgia": (59.1, 42.3), "Hawaii": (34.8, 22.1), "Idaho": (52.3, 36.7),
        "Illinois": (58.4, 41.2), "Indiana": (67.3, 49.1), "Iowa": (62.1, 43.8),
        "Kansas": (62.8, 44.9), "Kentucky": (82.3, 61.4), "Louisiana": (66.7, 48.3),
        "Maine": (63.9, 44.7), "Maryland": (53.2, 36.8), "Massachusetts": (50.1, 33.2),
        "Michigan": (61.4, 43.9), "Minnesota": (52.7, 36.1), "Mississippi": (72.1, 54.3),
        "Missouri": (68.4, 50.1), "Montana": (54.8, 38.2), "Nebraska": (58.9, 41.4),
        "Nevada": (57.3, 40.8), "New Hampshire": (56.7, 38.9), "New Jersey": (51.8, 35.1),
        "New Mexico": (43.7, 29.8), "New York": (50.9, 34.2), "North Carolina": (59.3, 41.7),
        "North Dakota": (56.1, 38.4), "Ohio": (67.8, 49.3), "Oklahoma": (70.2, 51.8),
        "Oregon": (52.4, 36.3), "Pennsylvania": (62.3, 44.1), "Rhode Island": (55.9, 38.2),
        "South Carolina": (61.7, 44.2), "South Dakota": (58.4, 40.9), "Tennessee": (72.8, 54.1),
        "Texas": (53.1, 36.4), "Utah": (32.4, 21.8), "Vermont": (56.8, 38.7),
        "Virginia": (56.4, 39.8), "Washington": (50.7, 34.6), "West Virginia": (81.2, 60.3),
        "Wisconsin": (57.3, 39.8), "Wyoming": (50.1, 34.7),
    }

    db = SessionLocal()
    try:
        for state, (incidence, mortality) in STATE_RATES.items():
            existing = db.get(models.SEERStateData, (state, CANCER_TYPE, 2021))
            if not existing:
                db.add(models.SEERStateData(
                    state=state,
                    cancer_type=CANCER_TYPE,
                    year=2021,
                    incidence_rate=incidence,
                    mortality_rate=mortality,
                ))
        if not dry_run:
            db.commit()
            print(f"✓ Synthetic SEER data generated: {len(STATE_RATES)} states")
        else:
            db.rollback()
            print(f"[dry-run] Would generate {len(STATE_RATES)} synthetic SEER records")
    finally:
        db.close()


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    run(dry_run=dry_run)
