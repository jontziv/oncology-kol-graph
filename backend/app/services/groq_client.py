from __future__ import annotations

"""
Groq API wrapper for generating compliant KOL engagement rationale.
Model: llama3-70b-8192 (free tier). Falls back gracefully if key is missing.
"""
from datetime import date
import json
from typing import Optional
from groq import Groq
from app.config import settings
from app import models

SYSTEM_PROMPT = """You are a medical affairs scientific engagement planner for an oncology launch team.
Your role is to produce compliant, science-first engagement rationale for key opinion leaders.

Rules:
- Never use promotional or sales language ("target", "convert", "prescriber", "promote")
- Frame all engagement around scientific exchange, data generation, and patient access
- Cite specific scores and data points from the provided context
- Always include a transparency note about any disclosed financial relationships
- Output must be suitable for review by a medical affairs compliance officer
- Output must be valid JSON with keys: rationale, engagement_type, compliance_note"""

USER_TEMPLATE = """Generate a scientific engagement rationale for the following oncology investigator.

Name: {name}
Institution: {institution}
Specialty: {specialty}
KOL Score: {kol_score}/100
Trial Activity: {trial_count} NSCLC trials ({recruiting_count} currently recruiting)
Publication Influence: {pub_count} publications, {total_citations} total citations
Geographic Coverage: Active in {state_count} state(s)
Disease Burden Context: {state} has an NSCLC incidence rate of {incidence_rate} per 100,000

Disclosed Financial Relationships (CMS Open Payments, public record):
{payments_summary}

Respond with a JSON object with exactly these keys:
- "rationale": 2-3 sentences, science-first engagement rationale
- "engagement_type": one of ["Advisory Board", "Phase III site activation", "Publication collaboration", "Medical education", "Data generation partnership"]
- "compliance_note": 1 sentence acknowledging disclosed relationships per FCPA/PhRMA guidelines"""


def _build_payments_summary(payments: list[models.Payment]) -> str:
    if not payments:
        return "No disclosed financial relationships on record."
    total = sum(p.amount_usd for p in payments)
    companies = {p.company_name for p in payments if p.company_name}
    natures = {p.nature_of_payment for p in payments if p.nature_of_payment}
    return (
        f"Total disclosed: ${total:,.2f} from {len(companies)} company/companies "
        f"({', '.join(list(natures)[:3])}{'...' if len(natures) > 3 else ''}). "
        f"Source: CMS Open Payments (public database)."
    )


def generate_rationale(
    inv: models.Investigator,
    seer_rate: Optional[float],
    db_session,
) -> dict[str, str]:
    """Call Groq to generate engagement rationale. Returns dict with rationale/engagement_type/compliance_note."""
    if not settings.groq_api_key:
        return _fallback_rationale(inv)

    from app import models as m
    recruiting_count = sum(
        1 for link in inv.trial_links
        if link.trial and link.trial.status and "recruiting" in link.trial.status.lower()
    )
    total_citations = sum(
        link.publication.citation_count or 0
        for link in inv.publication_links
        if link.publication
    )
    payments_summary = _build_payments_summary(inv.payments)
    inst_name = inv.institution.name if inv.institution else "Unknown Institution"
    state = inv.state or "Unknown"
    incidence = f"{seer_rate:.1f}" if seer_rate else "data not available"

    prompt = USER_TEMPLATE.format(
        name=inv.name,
        institution=inst_name,
        specialty=inv.specialty or "Oncology",
        kol_score=round(inv.kol_score, 1),
        trial_count=len(inv.trial_links),
        recruiting_count=recruiting_count,
        pub_count=len(inv.publication_links),
        total_citations=total_citations,
        state_count=inv.geographic_reach or 1,
        state=state,
        incidence_rate=incidence,
        payments_summary=payments_summary,
    )

    try:
        client = Groq(api_key=settings.groq_api_key)
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=600,
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content or "{}"
        result = json.loads(content)
        return {
            "rationale": result.get("rationale", ""),
            "engagement_type": result.get("engagement_type", "Advisory Board"),
            "compliance_note": result.get("compliance_note", ""),
        }
    except Exception:
        return _fallback_rationale(inv)


def _fallback_rationale(inv: models.Investigator) -> dict[str, str]:
    """Rule-based fallback when no Groq key is configured."""
    inst = inv.institution.name if inv.institution else "their institution"
    trial_count = len(inv.trial_links)
    pub_count = len(inv.publication_links)

    rationale = (
        f"Dr. {inv.name} at {inst} demonstrates strong NSCLC research engagement with "
        f"{trial_count} clinical trial participation(s) and {pub_count} related publication(s). "
        f"Their scientific profile supports meaningful data exchange on emerging treatment modalities "
        f"and potential site activation for future Phase II/III studies."
    )

    payment_total = inv.payment_total_usd or 0
    if payment_total > 0:
        compliance = (
            f"Disclosed financial relationships (CMS Open Payments, public record: ${payment_total:,.2f}) "
            f"are acknowledged per PhRMA Code guidelines and do not preclude compliant scientific engagement."
        )
    else:
        compliance = "No disclosed financial relationships on record per CMS Open Payments database."

    return {
        "rationale": rationale,
        "engagement_type": "Advisory Board" if inv.kol_score >= 60 else "Medical education",
        "compliance_note": compliance,
    }
