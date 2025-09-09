__author__ = "Adnan Karol"
__version__ = "1.0.0"
__maintainer__ = "Adnan Karol"
__email__ = "adnanmushtaq5@gmail.com"
__status__ = "DEV"

"""
🚀 Quantastic — Main Entry Point
"""

# Import Dependencies
import sys
import os
import time
import argparse
import logging  # Import the logging module
from concurrent.futures import ThreadPoolExecutor

# Suppress yfinance logs
logging.getLogger("yfinance").setLevel(logging.ERROR)

# Add the `src` directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from yfinance import Ticker
from utils.logger import log_info, log_success, log_error, log_warn
from utils.config import load_config, load_credentials, read_symbols
from utils.scoring import compute_scores_for_ticker
from utils.messaging import compose_message, send_telegram_message
from utils.cleaner import cleanup_generated_files
from utils.exceptions import ConfigError, DataFetchError

# Variables
CONFIG_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "../configs/config.json"
)
CREDENTIALS_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "../configs/credentials.json"
)
SLEEP_BETWEEN_CALLS = 0.5  # seconds


def validate_symbol(
    symbol: str, cfg: dict, retries: int = None, delisted_symbols: list = None
) -> bool:
    """
    Validates if a stock symbol exists on Yahoo Finance.

    Args:
        symbol (str): The stock symbol to validate.
        cfg (dict): Configuration dictionary.
        retries (int): Number of retries for validation (default: from config).
        delisted_symbols (list): List to store delisted symbols.

    Returns:
        bool: True if the symbol is valid, False otherwise.
    """
    retries = retries or cfg["validation"]["retries"]
    symbol_with_suffix = f"{symbol}.NS"  # Append .NS for NSE symbols
    error_message = None  # To store the final error message

    for attempt in range(1, retries + 1):
        try:
            ticker = Ticker(symbol_with_suffix)
            history = ticker.history(period="6mo")
            if history is None or history.empty:
                if "delisted" in str(history).lower():
                    if delisted_symbols is not None:
                        delisted_symbols.append(f"{symbol} (delisted)")
                    error_message = f"{symbol_with_suffix} is possibly delisted."
                    break
                continue
            return True  # Symbol is valid
        except Exception as e:
            if "401" in str(e):
                error_message = "HTTP Error 401: Unauthorized access."
                break
            error_message = str(e)
            if attempt < retries:
                time.sleep(attempt * 2)  # Exponential backoff

    # Log the final status after all retries
    if error_message:
        log_warn(
            f"⚠️ {symbol_with_suffix} could not be validated after {retries} retries: {error_message}"
        )
    if delisted_symbols is not None:
        delisted_symbols.append(f"{symbol} (invalid)")
    return False


def process_symbol(symbol: str, cfg: dict, skipped_symbols: list) -> dict:
    """
    Processes a single stock symbol.

    Args:
        symbol (str): The stock symbol to process.
        cfg (dict): Configuration dictionary.
        skipped_symbols (list): List to store skipped symbols.

    Returns:
        dict: The result of processing the symbol.
    """
    if not validate_symbol(symbol, cfg):
        skipped_symbols.append(symbol)
        return None
    try:
        return compute_scores_for_ticker(symbol, cfg)
    except Exception as e:
        log_error(f"❌ Unexpected error for {symbol}: {type(e).__name__}: {e}")
        skipped_symbols.append(symbol)
        return None


def main(args) -> None:
    """
    Main function for running the Quantastic stock scanner.

    Args:
        args: Parsed command-line arguments.

    Returns:
        None
    """
    try:
        log_info("🚀 Starting Quantastic...")
        cfg = load_config(CONFIG_PATH)
        creds = load_credentials(CREDENTIALS_PATH)

        # Ensure 'validation' key exists in cfg
        if "validation" not in cfg or "retries" not in cfg["validation"]:
            raise ConfigError("Missing 'validation' or 'retries' key in configuration.")

        symbols = read_symbols(
            os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "../data/symbols.csv"
            )
        )
        if not symbols:
            log_warn("⚠️ No symbols found in symbols.csv. Exiting.")
            return

        log_info(f"📊 Found {len(symbols)} symbol(s) to process.")

        results = []
        skipped_symbols = []
        delisted_symbols = []

        with ThreadPoolExecutor(max_workers=5) as executor:
            results = list(
                executor.map(lambda s: process_symbol(s, cfg, skipped_symbols), symbols)
            )
        results = [res for res in results if res]  # Filter out None results

        log_success("🎯 All stocks scored successfully!")

        if delisted_symbols:
            log_warn(f"⚠️ Delisted symbols: {', '.join(delisted_symbols)}")

        if skipped_symbols:
            log_warn(f"⚠️ Skipped symbols: {', '.join(skipped_symbols)}")

        if results:
            msg = compose_message(results, cfg, skipped_symbols)
            print(msg)

            if args.mode == "PROD":
                unique_chat_ids = set(creds["telegram"]["chat_ids"])
                for chat_id in unique_chat_ids:
                    send_telegram_message(creds["telegram"]["bot_token"], chat_id, msg)
                log_success("✅ Telegram messages sent successfully.")
            else:
                log_info("🛑 TEST mode: Telegram messages were not sent.")
        else:
            log_warn("⚠️ No valid results to process or send alerts for.")

        log_success("✅ Quantastic run completed.")
    except ConfigError as e:
        log_error(f"❌ Configuration error: {e}")
    except DataFetchError as e:
        log_error(f"❌ Data fetch error: {e}")
    except Exception as e:
        log_error(f"❌ Unexpected error: {e}")
    finally:
        cleanup_generated_files()


if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Run Quantastic stock scanner.")
    parser.add_argument(
        "--mode",
        type=str,
        choices=["TEST", "PROD"],
        default="PROD",
        help="Run mode: TEST (no messages sent) or PROD (messages sent). Default is PROD.",
    )
    args = parser.parse_args()

    main(args)
