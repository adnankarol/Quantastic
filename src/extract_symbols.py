"""
extract_symbols.py

This script fetches NSE and BSE stock symbols and saves a combined list to a CSV file
with duplicates removed.

Usage:
    python extract_symbols.py
"""

__author__ = "Adnan Karol + merged version"
__version__ = "1.0.1"
__maintainer__ = "Adnan Karol"
__email__ = "adnanmushtaq5@gmail.com"
__status__ = "DEV"

import os
import io
import time
import requests
import pandas as pd
from selenium import webdriver
from splinter import Browser
from utils.cleaner import cleanup_generated_files

# -------------------------
# Variables and Paths
# -------------------------
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

NSE_URL = "https://nsearchives.nseindia.com/content/equities/EQUITY_L.csv"
COMBINED_OUTPUT = os.path.join(DATA_DIR, "symbols.csv")
BSE_LINK = "https://www.bseindia.com/corporates/List_Scrips.html"


# -------------------------
# Functions
# -------------------------
def fetch_nse_symbols(url: str):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        session = requests.Session()
        session.headers.update(headers)
        response = session.get(url)
        response.raise_for_status()
        session.close()

        df_nse = pd.read_csv(io.BytesIO(response.content))
        print(f"✅ NSE symbols Extracted. Total: {len(df_nse)}")
        return df_nse["SYMBOL"].tolist()
    except Exception as e:
        print(f"❌ Failed to fetch NSE symbols: {e}")
        return []


def fetch_bse_security_ids(data_dir: str):
    try:
        prefs = {"download.default_directory": data_dir}
        options = webdriver.ChromeOptions()
        options.add_experimental_option("prefs", prefs)
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        browser = Browser("chrome", options=options, headless=True)
        browser.visit(BSE_LINK)

        browser.find_by_id("ddlsegment").select("Equity")
        browser.find_by_id("ddlstatus").select("Active")
        browser.find_by_id("btnSubmit").click()
        time.sleep(5)

        if not browser.is_element_present_by_text("Issuer Name", wait_time=10):
            raise Exception("BSE table did not load.")
        browser.find_by_id("lnkDownload").click()
        time.sleep(10)

        csv_file_path = os.path.join(data_dir, "Equity.csv")
        if os.path.exists(csv_file_path):
            df_bse = pd.read_csv(csv_file_path)
            print(f"✅ BSE Symbols Extracted. Total: {len(df_bse)}")
            return df_bse["Security Id"].tolist()
        else:
            print("❌ BSE download failed. File not found.")
            return []
    except Exception as e:
        print(f"❌ Failed to fetch BSE Security Ids: {e}")
        return []
    finally:
        browser.quit()


def merge_and_save_unique(list1, list2, output_file):
    combined = sorted(set(list1 + list2))
    pd.Series(combined).to_csv(output_file, index=False, header=False)
    print(f"✅ Combined symbols saved to {output_file}. Total unique: {len(combined)}")


# -------------------------
# Main Execution
# -------------------------
if __name__ == "__main__":
    nse_symbols = fetch_nse_symbols(NSE_URL)
    bse_symbols = fetch_bse_security_ids(DATA_DIR)
    merge_and_save_unique(nse_symbols, bse_symbols, COMBINED_OUTPUT)
    cleanup_generated_files()
