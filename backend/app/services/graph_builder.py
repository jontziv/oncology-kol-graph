from __future__ import annotations

"""
Builds graph JSON (nodes + links) from the relational DB.
All graph construction happens here — not in routers.
"""
from sqlalchemy.orm import Session
from app import models
from app.schemas import GraphNode, GraphLink, GraphResponse


def build_full_graph(
    db: Session,
    min_score: float = 0.0,
    state: str | None = None,
) -> GraphResponse:
    """Full graph: KOL nodes + institution nodes + relationship edges."""
    query = db.query(models.Investigator)
    if min_score > 0:
        query = query.filter(models.Investigator.kol_score >= min_score)
    if state:
        query = query.filter(models.Investigator.state == state)

    investigators = query.limit(100).all()  # cap for frontend perf — reduce for faster rendering

    nodes: list[GraphNode] = []
    links: list[GraphLink] = []
    seen_institutions: set[int] = set()

    for inv in investigators:
        nodes.append(GraphNode(
            id=f"kol-{inv.npi}",
            label=inv.name,
            type="kol",
            score=inv.kol_score,
            state=inv.state,
            institution=inv.institution.name if inv.institution else None,
        ))

        # Affiliated-with edge to institution
        if inv.institution_id and inv.institution_id not in seen_institutions:
            inst = inv.institution
            if inst:
                nodes.append(GraphNode(
                    id=f"inst-{inst.id}",
                    label=inst.name,
                    type="institution",
                    score=0.0,
                    state=inst.state,
                    institution=None,
                ))
                seen_institutions.add(inst.id)

        if inv.institution_id:
            links.append(GraphLink(
                source=f"kol-{inv.npi}",
                target=f"inst-{inv.institution_id}",
                type="affiliated_with",
            ))

    # Co-investigates edges: pairs of investigators on the same trial
    npi_set = {inv.npi for inv in investigators}
    trial_to_npis: dict[str, list[str]] = {}
    for inv in investigators:
        for link in inv.trial_links:
            trial_to_npis.setdefault(link.trial_nct_id, []).append(inv.npi)

    seen_co_inv: set[frozenset] = set()
    for nct_id, npis in trial_to_npis.items():
        for i, npi_a in enumerate(npis):
            for npi_b in npis[i + 1:]:
                pair = frozenset({npi_a, npi_b})
                if pair not in seen_co_inv and npi_a in npi_set and npi_b in npi_set:
                    links.append(GraphLink(
                        source=f"kol-{npi_a}",
                        target=f"kol-{npi_b}",
                        type="co_investigates",
                    ))
                    seen_co_inv.add(pair)

    # Co-authored edges: pairs of investigators sharing a publication
    pub_to_npis: dict[str, list[str]] = {}
    for inv in investigators:
        for link in inv.publication_links:
            pub_to_npis.setdefault(link.pmid, []).append(inv.npi)

    seen_co_auth: set[frozenset] = set()
    for pmid, npis in pub_to_npis.items():
        for i, npi_a in enumerate(npis):
            for npi_b in npis[i + 1:]:
                pair = frozenset({npi_a, npi_b})
                if pair not in seen_co_auth and npi_a in npi_set and npi_b in npi_set:
                    links.append(GraphLink(
                        source=f"kol-{npi_a}",
                        target=f"kol-{npi_b}",
                        type="co_authored",
                    ))
                    seen_co_auth.add(pair)

    return GraphResponse(nodes=nodes, links=links)


def build_egocentric_network(db: Session, npi: str) -> GraphResponse:
    """1-hop egocentric subgraph for a single KOL."""
    inv = db.query(models.Investigator).filter_by(npi=npi).first()
    if not inv:
        return GraphResponse(nodes=[], links=[])

    nodes: list[GraphNode] = [GraphNode(
        id=f"kol-{inv.npi}",
        label=inv.name,
        type="kol",
        score=inv.kol_score,
        state=inv.state,
        institution=inv.institution.name if inv.institution else None,
    )]
    links: list[GraphLink] = []

    # Institution node
    if inv.institution:
        nodes.append(GraphNode(
            id=f"inst-{inv.institution_id}",
            label=inv.institution.name,
            type="institution",
            score=0.0,
            state=inv.institution.state,
            institution=None,
        ))
        links.append(GraphLink(
            source=f"kol-{npi}",
            target=f"inst-{inv.institution_id}",
            type="affiliated_with",
        ))

    seen_npis: set[str] = {npi}

    # Co-investigators via shared trials
    for trial_link in inv.trial_links:
        for other_link in trial_link.trial.investigator_links:
            other_npi = other_link.investigator_npi
            if other_npi == npi:
                continue
            other_inv = db.query(models.Investigator).filter_by(npi=other_npi).first()
            if not other_inv:
                continue
            if other_npi not in seen_npis:
                nodes.append(GraphNode(
                    id=f"kol-{other_npi}",
                    label=other_inv.name,
                    type="kol",
                    score=other_inv.kol_score,
                    state=other_inv.state,
                    institution=other_inv.institution.name if other_inv.institution else None,
                ))
                seen_npis.add(other_npi)
            links.append(GraphLink(
                source=f"kol-{npi}",
                target=f"kol-{other_npi}",
                type="co_investigates",
            ))

    # Co-authors via shared publications
    for pub_link in inv.publication_links:
        for other_link in pub_link.publication.author_links:
            other_npi = other_link.investigator_npi
            if other_npi == npi:
                continue
            other_inv = db.query(models.Investigator).filter_by(npi=other_npi).first()
            if not other_inv:
                continue
            if other_npi not in seen_npis:
                nodes.append(GraphNode(
                    id=f"kol-{other_npi}",
                    label=other_inv.name,
                    type="kol",
                    score=other_inv.kol_score,
                    state=other_inv.state,
                    institution=other_inv.institution.name if other_inv.institution else None,
                ))
                seen_npis.add(other_npi)
            links.append(GraphLink(
                source=f"kol-{npi}",
                target=f"kol-{other_npi}",
                type="co_authored",
            ))

    return GraphResponse(nodes=nodes, links=links)
