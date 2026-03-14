import json
import time
import requests
from config import ADS_TOKEN, ADS_API_URL, REQUEST_DELAY

HEADERS = {
    "Authorization": f"Bearer {ADS_TOKEN}"
}


def query_ads_all(search_query, rows=200, max_records=10000):
    all_docs = []
    start = 0
    while True:
        params = {
            "q": search_query,
            "fl": "bibcode,title,year,doi,identifier,links_data,abstract",
            "rows": rows,
            "start": start
        }
        resp = requests.get(ADS_API_URL, headers=HEADERS, params=params)
        resp.raise_for_status()
        data = resp.json()
        docs = data["response"]["docs"]
        if not docs:
            print(f'query_ads_all(): No results for query: {search_query}')
            break
        all_docs.extend(docs)
        print(f"query_ads_all(): Retrieved {len(all_docs)} papers of {rows})")
        start += rows
        if start >= max_records:
            break
        time.sleep(REQUEST_DELAY)
    return all_docs

