__author__ = "Adnan Karol"
__version__ = "1.0.0"
__maintainer__ = "Adnan Karol"
__email__ = "adnanmushtaq5@gmail.com"
__status__ = "DEV"

import os
import pandas as pd
from typing import Any, Dict, List
from .logger import log_error
from .helpers import load_json


def load_config(path: str) -> Dict[str, Any]:
    """
    Loads the configuration from a JSON file.

    Args:
        path (str): The path to the configuration file.

    Returns:
        Dict[str, Any]: The loaded configuration as a dictionary.
    """
    return load_json(path)


def load_credentials(credentials_path: str) -> Dict[str, Any]:
    """
    Loads the credentials from a JSON file and replaces placeholders with environment variables.

    Args:
        credentials_path (str): The path to the credentials file.

    Returns:
        Dict[str, Any]: The loaded credentials as a dictionary.
    """
    creds = load_json(credentials_path)
    creds["telegram"]["bot_token"] = os.getenv(
        "TELEGRAM_BOT_TOKEN", creds["telegram"]["bot_token"]
    )
    return creds


def read_symbols(csv_path: str) -> List[str]:
    """
    Reads stock symbols from a CSV file.

    Args:
        csv_path (str): The path to the CSV file containing stock symbols.

    Returns:
        List[str]: A list of stock symbols.
    """
    try:
        df = pd.read_csv(csv_path, header=None, names=["symbol"])
        return df["symbol"].dropna().astype(str).str.strip().tolist()
    except Exception as e:
        log_error(f"Failed to read symbols: {e}")
        return []
