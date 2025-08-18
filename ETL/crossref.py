import requests

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


# Example:
if __name__ == "__main__":
    for doi in wiley_dois_2025_by_keyword("graphene", limit=20):
        print(doi)
