from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine
from app import models
from app.routers import graph, kols, institutions, payments, disease_burden, explain

# Create all tables on startup (idempotent)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Oncology KOL Intelligence Graph",
    description=(
        "Compliant commercial/medical intelligence API for NSCLC launch readiness. "
        "Data sourced from ClinicalTrials.gov, PubMed, CMS Open Payments, and NCI SEER."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(graph.router)
app.include_router(kols.router)
app.include_router(institutions.router)
app.include_router(payments.router)
app.include_router(disease_burden.router)
app.include_router(explain.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
