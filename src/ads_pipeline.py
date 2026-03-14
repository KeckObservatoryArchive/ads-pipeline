# ADS pipeline to extract content from PDF files

# No guarantees for:
# - broken equations
# - weird column merges
# - odd hyphenations
# ...but should be good enough for paper classifications
#
# extracting from ~10,000 papers takes est 5 to 15 min

import os
import re
import csv
import time
import random
from urllib.parse import quote
from ads_query import query_ads_all
from ads_downloader import download_pdf, get_pdf_urls
from extract_text import extract_two_column_text
from extract_text import extract_block_text

print("ads_pipeline: Working dir:", os.getcwd())

PDF_DIR = "data/pdf"
os.makedirs(PDF_DIR, exist_ok=True)

TEXT_DIR = "data/text"
os.makedirs(TEXT_DIR, exist_ok=True)

bibcode_list = 'ads_results.csv'

def run(csv_file):

    out = open("instrument_results.csv", "w")
    out.write("bibcode,instruments,keck_detected\n")

    # === read bibcodes from CSV and process each paper ===
    with open(csv_file) as f:
        reader = csv.DictReader(f)

        for row in reader:

            #bibcode = quote(row["bibcode"].strip())
            bibcode = row["bibcode"].strip()
            outfile = f"{PDF_DIR}/{bibcode}.pdf"

            # 1. download PDFs
            pdf_urls = get_pdf_urls(bibcode)
            success = False

            if pdf_urls is None:
                print(f"ads_pipeline::run(): No PDF URLs found for {bibcode}")
                continue

            for pdf_url in pdf_urls:
                print(f'ads_pipeline::run(): Trying {pdf_url}')
                if download_pdf(pdf_url, outfile):
                    success = True
                    break

            if not success:
                print(f"ads_pipeline::run(): PDF Download failed: {bibcode}")
                continue

            if not os.path.exists(outfile):
                print("ads_pipeline::run(): PDF missing, skipping:", outfile)
                continue

            # 1. extract text from PDF
            text = extract_block_text(outfile)

            # extra safety rate limit
            time.sleep(random.uniform(0.8, 1.4))



if __name__ == "__main__":
    run(bibcode_list)
