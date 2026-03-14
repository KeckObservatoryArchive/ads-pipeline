import csv
import requests
from urllib.parse import quote
from config import ADS_TOKEN, ADS_API_URL


HEADERS = {
    "Authorization": f"Bearer {ADS_TOKEN}"
}

# curl -H "Authorization: Bearer YOUR_TOKEN" \
# "https://api.adsabs.harvard.edu/v1/search/query?q=facility:%22W.%20M.%20Keck%20Observatory%22%20year:2000-2023%20property:refereed&fl=bibcode&rows=5"

# broad
#query = '(full:"keck observatory" OR full:"w. m. keck" OR full:hires OR full:deimos OR full:lris OR full:mosfire OR full:nirc2 OR full:nires OR full:nirspec OR full:osiris OR full:kpf OR full:kcwi OR full:esi) AND database:astronomy AND property:refereed AND doctype:article AND year:2000-2023'   # 21913
#query = '(full:"keck observatory" OR full:"w. m. keck" OR full:hires OR full:deimos OR full:lris OR full:mosfire OR full:nirc2 OR full:nires OR full:nirspec OR full:osiris OR full:kpf OR full:kcwi OR full:esi) AND database:astronomy AND property:refereed AND doctype:article AND year:2020-2023'   # 5951
#query = '(full:"keck observatory" OR full:"w. m. keck" OR full:hires OR full:deimos OR full:lris OR full:mosfire OR full:nirc2 OR full:nires OR full:nirspec OR full:osiris OR full:kpf OR full:kcwi OR full:esi) AND database:astronomy AND property:refereed AND doctype:article AND year:2023'        # 1581
query = 'database:"astronomy" AND property:"refereed" AND doctype:"article" AND year:"2022" (full:"keck observatory" OR full:"w. m. keck" OR full:hires OR full:deimos OR full:lris OR full:mosfire OR full:nirc2 OR full:nires OR full:nirspec OR full:osiris OR full:kpf OR full:kcwi OR full:esi)'     # 1404

rows = 200
start = 0
all_docs = []

#"fl": quote("bibcode"),
while True:
    params = {
        "q": query,
        "fl": "bibcode",
        "rows": rows,
        "start": start
    }
    resp = requests.get(ADS_API_URL, headers=HEADERS, params=params)
    if resp.status_code != 200:
        print("generate_ads_bibcodes(): ADS request failed:", resp.status_code)
        print(resp.text)
        break
    data = resp.json()
    if "response" not in data:
        print("generate_ads_bibcodes(): Unexpected ADS response:")
        print(data)
        break

    docs = data["response"]["docs"]
    if not docs:
        break

    all_docs.extend(docs)
    print(f"Fetched {len(all_docs)} bibcodes...")

    if len(docs) < rows:
        break

    start += rows

total = len(all_docs)
with open("ads_results.csv", "w", newline="") as f:

    writer = csv.writer(f)
    writer.writerow(["bibcode"])

    for d in all_docs:
        writer.writerow([d["bibcode"]])

print(f"\ngenerate_ads_bibcodes(): Saved {total} bibcodes to ads_results.csv")
