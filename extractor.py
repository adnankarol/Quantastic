from splinter import Browser
from selenium import webdriver
import pandas as pd
import time
import os

# Variables
data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
bse_link = "https://www.bseindia.com/corporates/List_Scrips.html"  # Corrected URL

# Ensure the data directory exists
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

# Set Chrome options
prefs = {"download.default_directory": data_dir}
options = webdriver.ChromeOptions()
options.add_experimental_option("prefs", prefs)
options.add_argument("--headless")  # Run in headless mode
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Initialize the browser
try:
    browser = Browser("chrome", options=options, headless=True)

    # Visit the BSE link
    browser.visit(bse_link)

    # Fill out form fields
    browser.find_by_id("ddlsegment").select("Equity")
    browser.find_by_id("ddlstatus").select("Active")

    # Submit the form
    browser.find_by_id("btnSubmit").click()

    # Wait for the table to load
    if not browser.is_element_present_by_text("Issuer Name", wait_time=10):
        raise Exception("Table did not load. Check the website or network connection.")
    time.sleep(5)

    # Download the file
    browser.find_by_id("lnkDownload").click()

    # Wait for the file to download
    time.sleep(10)

    # Load the downloaded CSV file into a Pandas DataFrame
    csv_file_path = os.path.join(data_dir, "Equity.csv")
    if os.path.exists(csv_file_path):
        df_bse = pd.read_csv(csv_file_path)
        # Save only the "Security Id" column to a new CSV file without the header
        output_file_path = os.path.join(data_dir, "security_ids.csv")
        df_bse[["Security Id"]].to_csv(output_file_path, index=False, header=False)
        print(f"✅ Security Ids saved to {output_file_path} without a header.")
    else:
        print("❌ Download failed. File not found.")

except Exception as e:
    print(f"❌ An error occurred: {e}")

finally:
    # Quit the browser
    browser.quit()
