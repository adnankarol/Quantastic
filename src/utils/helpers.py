import os
from typing import Any, Dict
import json


def resolve_path(relative_path: str) -> str:
    """
    Resolves a relative path to an absolute path.

    Args:
        relative_path (str): The relative path to resolve.

    Returns:
        str: The absolute path.
    """
    return os.path.abspath(os.path.join(os.path.dirname(__file__), relative_path))


def load_json(file_path: str) -> Dict[str, Any]:
    """
    Loads a JSON file and returns its content as a dictionary.

    Args:
        file_path (str): The path to the JSON file.

    Returns:
        Dict[str, Any]: The loaded JSON content.
    """
    with open(file_path, "r") as file:
        return json.load(file)
