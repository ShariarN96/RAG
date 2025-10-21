from __future__ import annotations

import os

import pandas as pd
import requests

OPENALEX_BASE = "https://api.openalex.org/works"
CROSSREF_BASE = "https://api.crossref.org/works"
DOI_RESOLVER = "https://doi.org/"

WILEY_PUBLISHER_ID = "P4310320503"  # OpenAlex publisher id for Wiley
WILEY_MEMBER_ID = 311  # Crossref member id for Wiley-Blackwell
USER_EMAIL = "YOU@EXAMPLE.COM"  # good etiquette for Crossref; optional for OpenAlex


def doi_resolves_to_wiley(doi: str, timeout: int = 15) -> bool:
    try:
        r = requests.head(DOI_RESOLVER + doi, allow_redirects=True, timeout=timeout)
        host = requests.utils.urlparse(r.url).netloc.lower()
        return "onlinelibrary.wiley.com" in host
    except Exception:
        return False


def openalex_random_wiley(
    query: str, from_date: str, to_date: str | None, n: int = 50
) -> list[str]:
    flt = [
        f"primary_location.source.host_organization:{WILEY_PUBLISHER_ID}",
        "type:journal-article",
        f"from_publication_date:{from_date}",
    ]
    if to_date:
        flt.append(f"to_publication_date:{to_date}")
    params = {
        "search": query,
        "filter": ",".join(flt),
        "sample": n,  # random N items each call
        "per_page": n,
    }
    r = requests.get(OPENALEX_BASE, params=params, timeout=60)
    r.raise_for_status()
    results = r.json().get("results", []) or []
    dois = []
    for w in results:
        doi = (w.get("ids") or {}).get("doi")
        if doi:
            dois.append(doi.lower())
    return dois


def crossref_random_wiley(
    query: str, year_from: int, year_to: int, n: int = 30
) -> list[str]:
    filters = [
        f"member:{WILEY_MEMBER_ID}",
        "type:journal-article",
        f"from-pub-date:{year_from}-01-01",
        f"until-pub-date:{year_to}-12-31",
    ]
    params = {
        "filter": ",".join(filters),
        "query.title": query,  # remove this if you want broader random
        "sample": n,  # random N items each call
        "select": "DOI,title",
        "mailto": USER_EMAIL,
    }
    headers = {"User-Agent": f"wiley-sampler/0.1 (mailto:{USER_EMAIL})"}
    r = requests.get(CROSSREF_BASE, params=params, headers=headers, timeout=30)
    r.raise_for_status()
    items = r.json().get("message", {}).get("items", []) or []
    dois = []
    for it in items:
        doi = it.get("DOI")
        if doi:
            dois.append(doi.lower())
    return dois


def find_random_wiley_dois(
    query: str,
    date_from: str = "2020-01-01",
    date_to: str | None = "2025-12-31",
    limit: int = 20,
    verify_wiley: bool = True,
) -> list[str]:
    # 1) Try OpenAlex for a random sample
    dois = openalex_random_wiley(query, date_from, date_to, n=limit)

    # 2) If too few, top up via Crossref random
    if len(dois) < limit:
        y_from = int(date_from[:4])
        y_to = int(date_to[:4]) if date_to else y_from
        extra = crossref_random_wiley(query, y_from, y_to, n=(limit - len(dois)))
        # combine & dedupe
        seen = set(dois)
        for d in extra:
            if d not in seen:
                dois.append(d)
                seen.add(d)
            if len(dois) >= limit:
                break

    # 3) Optional: verify each DOI actually lands on Wiley
    if verify_wiley:
        verified = []
        for d in dois:
            if doi_resolves_to_wiley(d):
                verified.append(d)
            if len(verified) >= limit:
                break
        return verified

    return dois[:limit]


def add_row(doi_list):
    df = pd.DataFrame(columns=["DOI"])
    for doi in doi_list:
        df.loc[len(df)] = doi

    df.to_csv("doi.csv", mode="a", header=not os.path.exists("doi.csv"), index=False)


def remove_duplicates(doi_list):
    df = pd.read_csv(doi_list)
    df = df.drop_duplicates()
    df.to_csv(doi_list, index=False)


def add_dois():
    QUERY = "detection of SARS covid-19"
    DATE_FROM = "2020-01-01"
    DATE_TO = "2025-12-31"
    LIMIT = 30
    VERIFY = True
    dois = find_random_wiley_dois(QUERY, DATE_FROM, DATE_TO, LIMIT, verify_wiley=VERIFY)

    add_row(dois)
    # remove_duplciates


# # ---- Run with your hard-coded defaults ----
# if __name__ == "__main__":
#     QUERY = "metal organic framework oxygen evolution reaction"
#     DATE_FROM = "2023-01-01"
#     DATE_TO = "2025-12-31"
#     LIMIT = 20
#     VERIFY = True
#     dois = find_random_wiley_dois(QUERY, DATE_FROM, DATE_TO, LIMIT, verify_wiley=VERIFY)
#     add_row(dois)
#     print(f"\nReturned {len(dois)} Wiley DOIs (randomized).")


BASE = "https://api.crossref.org/works"


def wiley_dois_2025_by_keyword(query, limit=5):
    """
    Fetch up to `limit` DOIs from Wiley-Blackwell (member:311), year 2025,
    filtered by a keyword query. Keeps it to a single, small request.
    """
    params = {
        "query": query,  # try 'high-entropy alloy', 'lithium ion battery', etc.
        "filter": "member:311,type:journal-article,from-pub-date:2025-01-01,until-pub-date:2025-12-31",
        "rows": limit,  # only get what we need
        "select": "DOI",  # DOIs only
        "sort": "published",
        "order": "desc",
    }
    headers = {"User-Agent": "wiley-doi-fetcher/0.1"}  # generic UA; no personal info
    r = requests.get(BASE, params=params, headers=headers, timeout=30)
    r.raise_for_status()
    items = r.json().get("message", {}).get("items", [])
    return [it["DOI"] for it in items if "DOI" in it]


for doi in wiley_dois_2025_by_keyword("detection of SARS covid-19", limit=50):
    print(doi)
