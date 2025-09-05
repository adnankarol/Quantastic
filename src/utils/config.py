__author__ = "Adnan Karol"
__version__ = "1.0.0"
__maintainer__ = "Adnan Karol"
__email__ = "adnanmushtaq5@gmail.com"
__status__ = "DEV"

import json
import pandas as pd
from src.utils.logger import log_error
from typing import Any, Dict, List


def load_config(path: str) -> Dict[str, Any]:
    """
    Loads the configuration from a JSON file.

    Args:
        path (str): The path to the configuration file.

    Returns:
        Dict[str, Any]: The loaded configuration as a dictionary.
    """
    with open(path, "r") as f:
        return json.load(f)


def load_credentials(credentials_path: str) -> Dict[str, Any]:
    """
    Loads the credentials from a JSON file.

    Args:
        credentials_path (str): The path to the credentials file.

    Returns:
        Dict[str, Any]: The loaded credentials as a dictionary.
    """
    with open(credentials_path, "r") as file:
        return json.load(file)


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
