__author__ = "Adnan Karol"
__version__ = "1.0.0"
__maintainer__ = "Adnan Karol"
__email__ = "adnanmushtaq5@gmail.com"
__status__ = "DEV"

"""
🚀 Quantastic — Main Entry Point
"""

# Import Dependencies
import time
import os
import shutil
from yfinance import Ticker
from utils.logger import log_info, log_success, log_debug, log_error, log_warn
from utils.config import load_config, load_credentials, read_symbols
from utils.scoring import compute_scores_for_ticker
from utils.messaging import compose_message, send_telegram_message
from utils.cleaner import cleanup_generated_files

# Variables
CONFIG_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "../configs/config.json"
)
CREDENTIALS_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "../configs/credentials.json"
)
SLEEP_BETWEEN_CALLS = 0.5  # seconds


def validate_symbol(symbol: str, retries: int = 3) -> bool:
    """
    Validates if a stock symbol exists on Yahoo Finance.

    Args:
        symbol (str): The stock symbol to validate.
        retries (int): Number of retries for validation.

    Returns:
        bool: True if the symbol is valid, False otherwise.
    """
    symbol_with_suffix = f"{symbol}.NS"  # Append .NS for NSE symbols
    for attempt in range(1, retries + 1):
        try:
            ticker = Ticker(symbol_with_suffix)
            if not ticker.history(period="6mo").empty:
                return True
            log_warn(
                f"⚠️ No data found for {symbol_with_suffix}. Attempt {attempt}/{retries}."
            )
        except Exception as e:
            log_error(
                f"❌ Validation failed for {symbol_with_suffix} on attempt {attempt}: {e}"
            )
        if attempt < retries:
            log_info(f"🔄 Retrying validation for {symbol_with_suffix}...")
    log_warn(f"⚠️ Skipping {symbol_with_suffix} after {retries} failed attempts.")
    return False


def main() -> None:
    """
    Main function for running the Quantastic stock scanner.

    This function loads the configuration, reads stock symbols, computes scores
    for each symbol, and sends a Telegram alert with the results.

    Args:
        None

    Returns:
        None
    """
    try:
        log_info("🚀 Starting Quantastic...")
        cfg = load_config(CONFIG_PATH)
        creds = load_credentials(CREDENTIALS_PATH)
        symbols = read_symbols(
            os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "../data/symbols.csv"
            )
        )

        results = []

        log_info(f"📊 Scanning {len(symbols)} symbol(s)...")
        for i, s in enumerate(symbols, start=1):
            log_info(f"🔍 [{i}/{len(symbols)}] Processing {s}...")
            if not validate_symbol(s):
                continue
            res = compute_scores_for_ticker(s, cfg)
            if res:
                results.append(res)
            time.sleep(SLEEP_BETWEEN_CALLS)

        log_success("🎯 All stocks scored successfully!")

        msg = compose_message(results, cfg)
        log_info("📤 Sending Telegram alert...")
        chat_ids = creds["telegram"][
            "chat_ids"
        ]  # Read chat IDs as a list from credentials
        for chat_id in chat_ids:
            send_telegram_message(creds["telegram"]["bot_token"], chat_id, msg)
        log_success("✅ Quantastic run completed.")
    except Exception as e:
        log_error(f"❌ An error occurred: {e}")
        raise
    finally:
        # Cleanup step to remove generated files
        cleanup_generated_files()


if __name__ == "__main__":
    main()
    cleanup_generated_files()
