import requests

BASE = "https://api.crossref.org/works"


# def wiley_dois_2025_by_keyword(query, limit=5):
#     base_params = {
#         "query": query,
#         "filter": "member:311,type:journal-article,from-pub-date:2025-01-01,until-pub-date:2025-12-31",
#         "rows": 0,
#     }
#     headers = {"User-Agent": "wiley-doi-fetcher/0.1"}
#     total = requests.get(BASE, params=base_params, headers=headers).json()["message"][
#         "total-results"
#     ]


#     offset = random.randint(0, max(0, total - limit))
#     params = base_params | {"rows": limit, "offset": offset, "select": "DOI"}
#     r = requests.get(BASE, params=params, headers=headers)
#     items = r.json()["message"]["items"]
#     return [it["DOI"] for it in items if "DOI" in it]


def wiley_dois_2025_by_keyword(query, limit=5):
    """
    Fetch up to `limit` random DOIs from Wiley-Blackwell (member:311), year 2025,
    filtered by a keyword query. Uses Crossref's `sample` parameter for randomness.
    """
    params = {
        "query": query,
        "filter": "member:311,type:journal-article,from-pub-date:2025-01-01,until-pub-date:2025-12-31",
        "sample": limit,  # 🔑 random sampling instead of deterministic rows
        # "select": "DOI",  # only fetch DOIs
    }
    headers = {"User-Agent": "wiley-doi-fetcher/0.1"}
    r = requests.get(BASE, params=params, headers=headers, timeout=30)
    r.raise_for_status()
    items = r.json().get("message", {}).get("items", [])
    # return [it["DOI"] for it in items if "DOI" in it]
    return items


def print_results():
    for doi in wiley_dois_2025_by_keyword("high-entropy alloy", limit=10):
        print(doi)


# Example:
if __name__ == "__main__":
    for doi in wiley_dois_2025_by_keyword("high-entropy alloy", limit=10):
        print(doi)

# items = wiley_dois_2025_by_keyword("high-entropy alloy", limit=10)

# x = items[0]

# columns = ["DOI", "title", "URL", "container-title", "created"]

# for i in columns:
#     print(x[i])

# x["DOI"]
# x["title"][0]
# x["URL"]
# x["container-title"]
# x["created"]["date-time"][0:10]
