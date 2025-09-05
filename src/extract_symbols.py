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


def extract_symbols(url: str, output_file: str) -> None:
    """
    Extracts stock symbols from the given URL and saves them to a CSV file.

    Args:
        url (str): The URL of the webpage to scrape.
        output_file (str): The path to the output CSV file.

    Returns:
        None
    """
    try:
        log_info(f"🌐 Sending GET request to {url}")
        # Send a GET request to the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes
        log_success(f"✅ Successfully fetched data from {url}")

        # Parse the HTML content
        soup = BeautifulSoup(response.text, "html.parser")

        # Find the table containing the stock symbols
        table = soup.find("table")
        if not table:
            log_error("❌ No table found on the webpage.")
            return

        # Extract table rows
        rows = table.find_all("tr")

        # Extract symbols
        symbols = []
        for row in rows[1:]:  # Skip the header row
            cols = row.find_all("td")
            if len(cols) >= 2:  # Ensure there are enough columns
                symbol = cols[1].text.strip()  # Extract from the second column
                if symbol:  # Ensure the symbol is not empty
                    symbols.append([symbol])  # Wrap symbol in a list for CSV format

        log_info(f"📊 Extracted {len(symbols)} symbols from the webpage.")

        # Save to a CSV file without a header
        with open(output_file, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(symbols)

        log_success(f"✅ Extracted {len(symbols)} symbols and saved to {output_file}")
        log_info("📂 CSV file is ready for use in the project.")

    except Exception as e:
        log_error(f"❌ An error occurred: {e}")


if __name__ == "__main__":
    extract_symbols(URL, OUTPUT_FILE)
    cleanup_generated_files()
