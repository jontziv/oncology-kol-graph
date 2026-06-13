-- ============================================================
-- Oncology KOL Intelligence Graph — Supabase Schema
-- Run this in: Supabase Dashboard → SQL Editor → New Query
-- ============================================================

-- 1. Institutions
CREATE TABLE IF NOT EXISTS institutions (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR NOT NULL UNIQUE,
    type        VARCHAR,
    city        VARCHAR,
    state       VARCHAR,
    lat         DOUBLE PRECISION,
    lon         DOUBLE PRECISION,
    trial_count INTEGER NOT NULL DEFAULT 0,
    kol_count   INTEGER NOT NULL DEFAULT 0,
    disease_burden_rate DOUBLE PRECISION
);
CREATE INDEX IF NOT EXISTS ix_institutions_state ON institutions (state);

-- 2. Investigators
CREATE TABLE IF NOT EXISTS investigators (
    id                   SERIAL PRIMARY KEY,
    npi                  VARCHAR NOT NULL UNIQUE,
    name                 VARCHAR NOT NULL,
    specialty            VARCHAR,
    institution_id       INTEGER REFERENCES institutions (id),
    state                VARCHAR,
    city                 VARCHAR,
    npi_source           VARCHAR NOT NULL DEFAULT 'clinicaltrials_derived',
    kol_score            DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    trial_score          DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    pub_score            DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    activity_score       DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    geographic_reach     INTEGER NOT NULL DEFAULT 0,
    geographic_reach_score DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    payment_total_usd    DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    payment_company_count INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS ix_investigators_npi   ON investigators (npi);
CREATE INDEX IF NOT EXISTS ix_investigators_state ON investigators (state);

-- 3. Trials
CREATE TABLE IF NOT EXISTS trials (
    nct_id          VARCHAR PRIMARY KEY,
    title           TEXT,
    phase           VARCHAR,
    status          VARCHAR,
    condition       TEXT,
    sponsor         VARCHAR,
    start_date      DATE,
    completion_date DATE,
    enrollment      INTEGER
);
CREATE INDEX IF NOT EXISTS ix_trials_status ON trials (status);

-- 4. Trial ↔ Investigator join
CREATE TABLE IF NOT EXISTS trial_investigators (
    trial_nct_id      VARCHAR NOT NULL REFERENCES trials (nct_id),
    investigator_npi  VARCHAR NOT NULL REFERENCES investigators (npi),
    role              VARCHAR,
    PRIMARY KEY (trial_nct_id, investigator_npi)
);

-- 5. Publications
CREATE TABLE IF NOT EXISTS publications (
    pmid           VARCHAR PRIMARY KEY,
    title          TEXT,
    journal        VARCHAR,
    year           INTEGER,
    citation_count INTEGER NOT NULL DEFAULT 0,
    abstract       TEXT
);
CREATE INDEX IF NOT EXISTS ix_publications_year ON publications (year);

-- 6. Publication ↔ Investigator join
CREATE TABLE IF NOT EXISTS publication_authors (
    pmid             VARCHAR NOT NULL REFERENCES publications (pmid),
    investigator_npi VARCHAR NOT NULL REFERENCES investigators (npi),
    author_order     INTEGER,
    PRIMARY KEY (pmid, investigator_npi)
);

-- 7. CMS Open Payments
CREATE TABLE IF NOT EXISTS payments (
    id               SERIAL PRIMARY KEY,
    investigator_npi VARCHAR REFERENCES investigators (npi),
    company_name     VARCHAR,
    amount_usd       DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    nature_of_payment VARCHAR,
    year             INTEGER,
    record_id        VARCHAR UNIQUE
);
CREATE INDEX IF NOT EXISTS ix_payments_investigator_npi ON payments (investigator_npi);

-- 8. SEER state disease burden
CREATE TABLE IF NOT EXISTS seer_state_data (
    state        VARCHAR NOT NULL,
    cancer_type  VARCHAR NOT NULL DEFAULT 'Lung and Bronchus',
    year         INTEGER NOT NULL DEFAULT 2021,
    incidence_rate DOUBLE PRECISION,
    mortality_rate DOUBLE PRECISION,
    PRIMARY KEY (state, cancer_type, year)
);

-- 9. Groq explanation cache
CREATE TABLE IF NOT EXISTS kol_explanations (
    npi              VARCHAR PRIMARY KEY REFERENCES investigators (npi),
    rationale        TEXT,
    engagement_type  VARCHAR,
    compliance_note  TEXT,
    generated_at     DATE
);
