"""
extract_symbols.py

This script scrapes NSE stock symbols from a predefined URL and saves them to a CSV file.
It also includes a cleanup function to remove generated files like __pycache__.

Usage:
    python extract_symbols.py
"""

__author__ = "Adnan Karol"
__version__ = "1.0.0"
__maintainer__ = "Adnan Karol"
__email__ = "adnanmushtaq5@gmail.com"
__status__ = "DEV"

# Import Dependencies
import requests
from bs4 import BeautifulSoup
import csv
import os
import shutil
import time
from utils.logger import log_info, log_success, log_debug, log_error
from utils.cleaner import cleanup_generated_files

# Variables
URL = "https://stockanalysis.com/list/nse-india/"
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data")
OUTPUT_FILE = os.path.join(DATA_DIR, "symbols.csv")

# Ensure the data directory exists
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)
    log_info(f"📂 Created data directory at {DATA_DIR}")


def extract_symbols(url: str, output_file: str, retries: int = 3) -> None:
    """
    Extracts stock symbols from the given URL and saves them to a CSV file.

    Args:
        url (str): The URL of the webpage to scrape.
        output_file (str): The path to the output CSV file.
        retries (int): Number of retries for network requests.

    Returns:
        None
    """
    attempt = 0
    while attempt < retries:
        try:
            log_info(
                f"🌐 Sending GET request to {url} (Attempt {attempt + 1}/{retries})"
            )
            response = requests.get(url)
            response.raise_for_status()  # Raise an error for bad status codes
            log_success(f"✅ Successfully fetched data from {url}")

            soup = BeautifulSoup(response.text, "html.parser")
            table = soup.find("table")
            if not table:
                log_error("❌ No table found on the webpage.")
                return

            rows = table.find_all("tr")
            if not rows:
                log_error("❌ No rows found in the table.")
                return

            symbols = []
            for row in rows[1:]:  # Skip the header row
                cols = row.find_all("td")
                if len(cols) >= 2:
                    symbol = cols[1].text.strip()
                    if symbol:
                        symbols.append([symbol])

            log_info(f"📊 Extracted {len(symbols)} symbols from the webpage.")

            with open(output_file, "w", newline="") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerows(symbols)

            log_success(
                f"✅ Extracted {len(symbols)} symbols and saved to {output_file}"
            )
            return
        except requests.exceptions.RequestException as e:
            log_error(f"❌ Network error: {e}")
            attempt += 1
            if attempt < retries:
                wait_time = attempt * 2
                log_info(f"🔄 Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                log_error("❌ Failed to fetch symbols after multiple attempts.")
                return
        except Exception as e:
            log_error(f"❌ An unexpected error occurred: {e}")
            return


if __name__ == "__main__":
    extract_symbols(URL, OUTPUT_FILE)
    cleanup_generated_files()
