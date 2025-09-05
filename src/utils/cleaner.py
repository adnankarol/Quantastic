__author__ = "Adnan Karol"
__version__ = "1.0.0"
__maintainer__ = "Adnan Karol"
__email__ = "adnanmushtaq5@gmail.com"
__status__ = "DEV"

# Import Dependencies
import os
import shutil
from logger import log_info, log_success, log_error  # Import logger methods

# Define the root directory of the project
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))


def cleanup_generated_files() -> None:
    """
    Recursively removes all __pycache__ directories and .DS_Store files in the project.

    Args:
        None

    Returns:
        None
    """
    try:
        for root, dirs, files in os.walk(ROOT_DIR):  # Start from the root directory
            # Remove __pycache__ directories
            if "__pycache__" in dirs:
                pycache_path = os.path.join(root, "__pycache__")
                shutil.rmtree(pycache_path)

            # Remove .DS_Store files
            for file in files:
                if file == ".DS_Store":
                    ds_store_path = os.path.join(root, file)
                    os.remove(ds_store_path)

        log_success("🧹 Cleaned up generated files.")
    except Exception as e:
        log_error(f"❌ Failed to clean up generated files: {e}")
