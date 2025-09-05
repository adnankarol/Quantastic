__author__ = "Adnan Karol"
__version__ = "1.0.0"
__maintainer__ = "Adnan Karol"
__email__ = "adnanmushtaq5@gmail.com"
__status__ = "DEV"

# Import Dependencies
import requests
import json
import os
from cleaner import cleanup_generated_files

# Variables
CREDENTIALS_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "../../configs/credentials.json"
)
with open(CREDENTIALS_PATH, "r") as file:
    credentials = json.load(file)
    BOT_TOKEN = credentials["telegram"]["bot_token"]

URL = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"


def fetch_chat_ids():
    """
    Fetch and print unique chat IDs along with names and usernames from Telegram bot updates.

    Args:
        None

    Returns:
        None
    """
    # Fetch updates from the bot
    response = requests.get(URL)
    data = response.json()

    # Track printed chat IDs to avoid duplicates
    printed_chat_ids = set()

    if "result" in data:
        for update in data["result"]:
            chat_id = update["message"]["chat"]["id"]
            if chat_id not in printed_chat_ids:
                first_name = update["message"]["chat"].get("first_name", "Unknown")
                username = update["message"]["chat"].get("username", "No username")
                print(f"Chat ID: {chat_id}, Name: {first_name}, Username: {username}")
                printed_chat_ids.add(chat_id)
    else:
        print("No messages found. Ask your friend to send a message to the bot.")


if __name__ == "__main__":
    fetch_chat_ids()
    cleanup_generated_files()
