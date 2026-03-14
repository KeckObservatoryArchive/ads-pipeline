import os
import json
import time
import requests
from pathlib import Path
from urllib.parse import quote
from pdf_utils import valid_pdf
from config import ADS_TOKEN, ADS_API_URL

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "application/pdf,application/octet-stream,text/html;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Authorization": f"Bearer {ADS_TOKEN}",
    "Referer": "https://ui.adsabs.harvard.edu/",
    "Connection": "keep-alive"
}

#ADS_API_URL = "https://api.adsabs.harvard.edu/v1/search/query"


def get_pdf_urls(bibcode):

    #ebibcode = quote(bibcode)
    params = {
        "q": f'bibcode:"{bibcode}"',
        "fl": "links_data",
        "rows": 1
    }

    time.sleep(0.5)

    resp = requests.get(ADS_API_URL, headers=HEADERS, params=params)
    #print(resp.json())
    resp.raise_for_status()

    docs = resp.json()["response"]["docs"]

    if not docs:
        print(f"ads_downloader::get_pdf_urls(): No ADS record for {bibcode}")
        return None
    data = docs[0]

    links_raw = data.get("links_data")

    if not links_raw:
        return None

    links = []
    #links = get_pdf_urls()

    # case 1: ADS returned a list of strings or dicts
    if isinstance(links_raw, list):
        print(f'ads_downloader::get_pdf_urls(): [links_raw is a list] For {bibcode}: {links_raw} of ** TYPE ** {type(links_raw)}')
        for item in links_raw:
            if isinstance(item, str):
                print(f'ads_downloader::get_pdf_urls(): [element in links_raw is a str]For {bibcode}, got links_data item: {item} and ** TYPE ** is: {type(item)}')
                links.append(json.loads(item))
            elif isinstance(item, dict):
                print(f'ads_downloader::get_pdf_urls(): [element in links_raw is a dict]For {bibcode}, got links_data item: {item} and ** TYPE ** is: {type(item)}')
                links.append(item)

    # case 2: ADS returned a JSON string
    elif isinstance(links_raw, str):
        print(f'ads_downloader::get_pdf_urls(): [links_raw is a str] For {bibcode}: {links_raw} of ** TYPE ** {type(links_raw)}')
        links = json.loads(links_raw)


    # extract urls from links_data
    urls = []
    for link in links:
        url = link.get("url", "")

        #if link.get("type") != "pdf":
            #print(f"Skipping non-PDF link for {bibcode}: {url} (type: {link.get('type')})")
            #continue

        # prefer arXiv if available
        if url and "arxiv.org" in url:

            # handle old and new arXiv formats
            arxiv_id = url.split("arxiv.org/")[-1]

            if arxiv_id.startswith("abs/"):
                arxiv_id = arxiv_id[4:]

            urls.append(f"https://arxiv.org/pdf/{arxiv_id}.pdf")
        
        elif link.get("type") in ["pdf", "PUB_PDF", "EPRINT_PDF"]:
            urls.append(url)

    urls.sort(key=lambda x: "arxiv" not in x)
    return urls


def looks_like_pdf(path):
    """
    Quick header check before expensive parsing.
    """
    with open(path, "rb") as f:
        return f.read(5) == b"%PDF-"


def download_pdf(url, outpath, retries=3, delay=2):
    """
    Download a PDF from a given URL and validate it.
    """

    outpath = Path(outpath)
    if outpath.exists() and valid_pdf(outpath):
        print(f"ads_downloader::download_pdf(): Outdir Path Already Exists: {outpath}")
        return True

    for attempt in range(retries):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=60, allow_redirects=True)

            if resp.status_code != 200:
                print(f"ads_downloader::download_pdf(): HTTP error: {resp.status_code}")
                print(f"ads_downloader::download_pdf(): URL returned: {resp.url}")
                time.sleep(delay * 2)
                continue
    
            ctype = resp.headers.get("content-type", "").lower()
    
            if "text/html" in ctype:
                print(f"ads_pipeline::download_pdf(): HTML page returned instead of PDF: {resp.url}")
                return False
    
            if "pdf" not in ctype and not resp.content.startswith(b"%PDF"):
                print("ads_downloader::download_pdf(): File is not a PDF")
                print("ads_downloader::download_pdf(): Content-Type:", ctype)
                print("ads_downloader::download_pdf(): URL returned:", resp.url)
                return False
    
            with open(outpath, "wb") as f:
                f.write(resp.content)
    
            if not looks_like_pdf(outpath):
                print("ads_downloader::download_pdf(): File does not start with PDF header:", outpath)
                if os.path.exists(outpath):
                    os.remove(outpath)
                return False
    
            if not valid_pdf(outpath):
                print("ads_downloader::download_pdf(): Corrupt PDF:", outpath)
                if os.path.exists(outpath):
                    os.remove(outpath)
                return False
    
            print(f"ads_downloader::download_pdf(): Downloaded OK: {outpath}")
            return True
    
        except Exception as e:
            print(f"ads_downloader::download_pdf(): Download error: {e}")
    
        time.sleep(delay)
    
    print(f"ads_downloader::download_pdf(): FAILED: {url}")
    return False

