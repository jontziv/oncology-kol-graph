# Oncology Launch Intelligence Graph

**Prioritising Scientific Engagement for a Hypothetical NSCLC Launch**

A compliant commercial/medical intelligence application demonstrating how a medical affairs team could use transparent public data to identify oncology investigators with high scientific engagement potential, understand institutional trial networks, and generate compliant engagement rationale.

> Portfolio demo · Hypothetical launch scenario · Not for clinical or commercial use

---

## Features

| Feature | Description |
|---|---|
| **KOL Network Graph** | Force-directed graph of investigator relationships (co-investigates, co-authors, affiliated-with) |
| **Composite KOL Scoring** | Weighted score from trial activity, publication influence, recency, and geographic reach |
| **Institution Rankings** | Sortable institution table with trial density and disease burden overlay |
| **Disease Burden Map** | Choropleth of SEER lung cancer incidence rates by US state |
| **Transparency View** | CMS Open Payments explorer with compliance framing |
| **Engagement Rationale** | Groq + Llama-powered science-first engagement rationale (compliant language) |

---

## Tech Stack

- **Backend**: FastAPI + SQLAlchemy 2.0 (SQLite / PostgreSQL)
- **Frontend**: React 18 + Vite + TypeScript (strict) + Tailwind CSS
- **Graph viz**: react-force-graph-2d (D3/WebGL)
- **Map**: react-simple-maps + d3-scale-chromatic
- **AI**: Groq API (free) — llama3-70b-8192
- **Data**: ClinicalTrials.gov, PubMed, CMS Open Payments, NCI SEER

---

## Data Sources (All Public)

| Source | Use | License |
|---|---|---|
| [ClinicalTrials.gov](https://clinicaltrials.gov) (NIH/NLM) | Investigators, trials, sites | Public domain |
| [PubMed](https://pubmed.ncbi.nlm.nih.gov) (NCBI/NLM) | Publications, citation counts | Public domain |
| [CMS Open Payments](https://openpaymentsdata.cms.gov) | Pharmaceutical payment disclosures | Public domain |
| [NCI SEER](https://statecancerprofiles.cancer.gov) | State-level lung cancer incidence/mortality | Public domain |

---

## Local Setup

### Prerequisites

- Python 3.9+ (system Python, not Anaconda — see note below)
- Node.js 18+
- [Groq API key](https://console.groq.com) (free)
- NCBI API key (optional — increases PubMed rate limit)

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your GROQ_API_KEY

# Run data ingestion (takes 5–20 min)
python ingestion/run_all.py

# Skip slow PubMed step for quick first run:
# python ingestion/run_all.py --skip-pubmed

# Start API server
uvicorn app.main:app --reload --port 8000
```

> **Note**: On macOS with Anaconda, use `/usr/bin/python3` to create the venv — Anaconda's Python has a broken SQLite dylib on some macOS versions.

### Frontend

```bash
cd frontend
npm install
npm run dev
# → http://localhost:5173
```

### Verify

After ingestion, check the API:
```bash
curl http://localhost:8000/api/kols?sort_by=kol_score | python3 -m json.tool | head -40
curl http://localhost:8000/health
```

---

## Scoring Methodology

KOL scores are relative (0–100) within the ingested cohort, not absolute benchmarks.

```
KOL Score = 0.35 × Trial Score
           + 0.30 × Publication Score
           + 0.20 × Activity Score (recency-weighted)
           + 0.15 × Geographic Reach Score

Trial Score: Σ phase_weight × status_weight, normalised to cohort max
  phase_weights: Phase 3 = 3.0, Phase 2 = 2.0, Phase 1 = 1.0
  status_weights: Recruiting = 1.5, Active = 1.0, Completed = 0.7

Publication Score: Σ log1p(citation_count), normalised to cohort max

Activity Score: recent trials (≤3 years) weighted 2×, older 1×

Geographic Reach: distinct states across trial network, capped at 10 states = 100
```

Scores are recomputed on every ingestion run.

---

## Compliance & Framing

This tool is designed to demonstrate **medical affairs scientific engagement planning**, not sales targeting:

- Payment data is sourced exclusively from CMS Open Payments (public record) and labelled as such
- AI-generated rationale is always watermarked: *"AI-generated draft — requires Medical Affairs review before use"*
- The word "target" is never used — investigators are "accounts" or "investigators"
- All engagement framing is science-first: trial participation, publication collaboration, data generation

---

## Portfolio Framing

> "Oncology Launch Intelligence Graph: Prioritising Scientific Engagement for a Hypothetical NSCLC Launch"

This project demonstrates cross-functional commercial pharma thinking:

- **Data engineering**: multi-source public API ingestion with fuzzy entity matching
- **Scoring**: explainable, weighted composite scores
- **Compliance**: transparent framing of payment relationships
- **Product surface**: field-usable account intelligence with AI explainability
- **Graph analytics**: investigator network construction from relational data

Target roles: **Senior PM (Commercial Analytics)**, **Medical Affairs Strategy**, **Commercial Data Science Lead**
