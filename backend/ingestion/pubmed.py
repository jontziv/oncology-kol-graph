from __future__ import annotations

"""
Pull NSCLC publications from PubMed E-utilities.
Fuzzy-matches authors against known investigators from the DB.
Run time: ~5-15 min (citation fetching is slow).
"""
import asyncio
import sys
import os
import xml.etree.ElementTree as ET
from math import ceil

import httpx
from rapidfuzz import fuzz
from sqlalchemy.orm import Session

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app.database import SessionLocal, engine
from app import models
from app.config import settings

EUTILS_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
MAX_RESULTS = 2000
BATCH_SIZE = 100
FUZZY_THRESHOLD = 88  # rapidfuzz score 0-100


def _api_key_param() -> dict:
    if settings.ncbi_api_key:
        return {"api_key": settings.ncbi_api_key}
    return {}


async def search_pmids(client: httpx.AsyncClient, term: str, retmax: int) -> list[str]:
    resp = await client.get(
        f"{EUTILS_BASE}/esearch.fcgi",
        params={"db": "pubmed", "term": term, "retmax": retmax, "retmode": "json", **_api_key_param()},
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    return data.get("esearchresult", {}).get("idlist", [])


async def fetch_articles_xml(client: httpx.AsyncClient, pmids: list[str]) -> ET.Element:
    resp = await client.get(
        f"{EUTILS_BASE}/efetch.fcgi",
        params={"db": "pubmed", "id": ",".join(pmids), "rettype": "xml", "retmode": "xml", **_api_key_param()},
        timeout=60,
    )
    resp.raise_for_status()
    return ET.fromstring(resp.content)


async def fetch_citation_count(client: httpx.AsyncClient, pmid: str) -> int:
    """Count how many PubMed articles cite this PMID via elink."""
    resp = await client.get(
        f"{EUTILS_BASE}/elink.fcgi",
        params={
            "dbfrom": "pubmed",
            "linkname": "pubmed_pubmed_citedin",
            "id": pmid,
            "retmode": "json",
            **_api_key_param(),
        },
        timeout=20,
    )
    if resp.status_code != 200:
        return 0
    data = resp.json()
    try:
        link_sets = data["linksets"][0]["linksetdbs"]
        for ls in link_sets:
            if ls.get("linkname") == "pubmed_pubmed_citedin":
                return len(ls.get("links", []))
    except (KeyError, IndexError):
        pass
    return 0


def parse_articles(root: ET.Element) -> list[dict]:
    articles = []
    for article_el in root.findall(".//PubmedArticle"):
        medline = article_el.find("MedlineCitation")
        if medline is None:
            continue

        pmid_el = medline.find("PMID")
        pmid = pmid_el.text if pmid_el is not None else None
        if not pmid:
            continue

        article = medline.find("Article")
        if article is None:
            continue

        title_el = article.find("ArticleTitle")
        title = (title_el.text or "").strip() if title_el is not None else None

        journal_el = article.find("Journal/Title")
        journal = journal_el.text if journal_el is not None else None

        year_el = article.find("Journal/JournalIssue/PubDate/Year")
        year = int(year_el.text) if year_el is not None and year_el.text else None

        abstract_el = article.find("Abstract/AbstractText")
        abstract = abstract_el.text if abstract_el is not None else None

        authors = []
        for auth_el in article.findall("AuthorList/Author"):
            last = auth_el.findtext("LastName", "")
            fore = auth_el.findtext("ForeName", "")
            affil = auth_el.findtext("AffiliationInfo/Affiliation", "")
            if last:
                authors.append({"last": last, "fore": fore, "affiliation": affil})

        articles.append({
            "pmid": pmid,
            "title": title,
            "journal": journal,
            "year": year,
            "abstract": abstract,
            "authors": authors,
        })
    return articles


def build_investigator_index(db: Session) -> list[dict]:
    """Build a lookup list for fuzzy name matching."""
    investigators = db.query(
        models.Investigator.npi, models.Investigator.name
    ).all()
    index = []
    for npi, name in investigators:
        parts = name.strip().split()
        last = parts[-1] if parts else ""
        fore = parts[0] if len(parts) > 1 else ""
        index.append({"npi": npi, "name": name, "last": last.lower(), "fore": fore.lower()})
    return index


def match_author(author: dict, inv_index: list[dict]) -> str | None:
    """Return investigator NPI if author fuzzy-matches above threshold."""
    a_last = author["last"].lower()
    a_fore = author["fore"].lower()

    for inv in inv_index:
        # Quick last-name gate before expensive full-name score
        if fuzz.ratio(a_last, inv["last"]) < 70:
            continue
        full_query = f"{a_last} {a_fore}"
        full_candidate = f"{inv['last']} {inv['fore']}"
        score = fuzz.token_sort_ratio(full_query, full_candidate)
        if score >= FUZZY_THRESHOLD:
            return inv["npi"]
    return None


async def run(dry_run: bool = False) -> None:
    models.Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    print("Building investigator name index...")
    inv_index = build_investigator_index(db)
    print(f"  {len(inv_index)} investigators loaded")

    if not inv_index:
        print("No investigators in DB — run clinicaltrials.py first.")
        db.close()
        return

    print(f"\nSearching PubMed for NSCLC publications (max {MAX_RESULTS})...")
    async with httpx.AsyncClient() as client:
        pmids = await search_pmids(client, "NSCLC[Title/Abstract] OR \"non-small cell lung cancer\"[Title/Abstract]", MAX_RESULTS)
        print(f"  Found {len(pmids)} PMIDs")

        matched_pubs = 0
        for batch_start in range(0, len(pmids), BATCH_SIZE):
            batch = pmids[batch_start:batch_start + BATCH_SIZE]
            print(f"  Fetching articles {batch_start + 1}–{batch_start + len(batch)}...")

            try:
                root = await fetch_articles_xml(client, batch)
            except Exception as e:
                print(f"  Warning: batch fetch failed ({e}), skipping")
                continue

            articles = parse_articles(root)

            for art in articles:
                # Only store publications with at least one matched investigator
                matched_npis: list[tuple[str, int]] = []  # (npi, author_order)
                for order, auth in enumerate(art["authors"], start=1):
                    npi = match_author(auth, inv_index)
                    if npi:
                        matched_npis.append((npi, order))

                if not matched_npis:
                    continue

                # Fetch citation count (slow — rate-limited)
                if not dry_run:
                    try:
                        citations = await fetch_citation_count(client, art["pmid"])
                        await asyncio.sleep(0.11)  # stay within NCBI rate limit (10 req/s with key)
                    except Exception:
                        citations = 0
                else:
                    citations = 0

                # Upsert publication
                existing_pub = db.get(models.Publication, art["pmid"])
                if not existing_pub:
                    db.add(models.Publication(
                        pmid=art["pmid"],
                        title=art["title"],
                        journal=art["journal"],
                        year=art["year"],
                        citation_count=citations,
                        abstract=art["abstract"],
                    ))
                    db.flush()

                for npi, order in matched_npis:
                    existing_link = (
                        db.query(models.PublicationAuthor)
                        .filter_by(pmid=art["pmid"], investigator_npi=npi)
                        .first()
                    )
                    if not existing_link:
                        db.add(models.PublicationAuthor(
                            pmid=art["pmid"],
                            investigator_npi=npi,
                            author_order=order,
                        ))

                matched_pubs += 1

            if not dry_run:
                db.commit()

            await asyncio.sleep(0.5)

    if dry_run:
        db.rollback()
        print(f"\n[dry-run] Would have matched ~{matched_pubs} publications. No data written.")
    else:
        pub_count = db.query(models.Publication).count()
        print(f"\n✓ PubMed ingestion complete: {pub_count} publications stored")

    db.close()


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    asyncio.run(run(dry_run=dry_run))
