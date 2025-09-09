__author__ = "Adnan Karol"
__version__ = "1.0.0"
__maintainer__ = "Adnan Karol"
__email__ = "adnanmushtaq5@gmail.com"
__status__ = "DEV"

from typing import Any, Dict, List
from telegram import Bot
from src.utils.logger import log_success, log_error, log_warn
from datetime import datetime
import pandas as pd
import html  # For escaping HTML content


def compose_message(results: list, cfg: dict, skipped_symbols: list) -> str:
    """
    Composes a message summarizing the stock analysis results in a message format with enhanced recommendations.

    Args:
        results (list): List of dictionaries containing stock scores.
        cfg (dict): Configuration dictionary.
        skipped_symbols (list): List of skipped symbols.

    Returns:
        str: The composed message.
    """
    try:
        if not results:
            raise ValueError("No results to compose a message.")

        # Filter stocks above the buy_threshold
        buy_threshold = cfg["thresholds"]["buy_threshold"]
        filtered_results = [
            res for res in results if res["final_score"] >= buy_threshold
        ]

        if not filtered_results:
            return "<b>🚀 Quantastic — Stock Analysis Results</b>\n\n⚠️ No stocks met the buy threshold.\n"

        # Sort results by final score in descending order
        filtered_results = sorted(
            filtered_results, key=lambda x: x["final_score"], reverse=True
        )

        # Prepare the message header
        message = "<b>🚀 Quantastic — Stock Analysis Results</b>\n\n"
        message += f"📊 Processed <b>{len(results)}</b> stocks from NSE.\n\n"
        message += "<b>🎯 Quantastic Recommends to Check these Stocks: </b>\n\n"

        # Add stock details
        avg_price_duration = cfg["scoring"].get("avg_price_duration", 30)
        for result in filtered_results[: cfg["scoring"]["top_n_watch"]]:
            try:
                message += (
                    f"🏷️ <b>{result['symbol']}</b>\n"
                    f"   • 🏆 Final Score: <b>{round(result['final_score'],1)}</b>\n"
                    f"   • 📈 Tech Score: {round(result['tech_score'],1)}\n"
                    f"   • 💼 Fund Score: {round(result['fund_score'],1)}\n"
                    f"   • 💰 Last Close: ₹{round(result.get('last_close', 'N/A'),1)}\n"
                    f"   • 📊 Avg Price ({avg_price_duration}d): ₹{round(result.get('avg_price', 'N/A'),1)}\n\n"
                )
            except KeyError as e:
                log_warn(
                    f"⚠️ Missing key in result for {result.get('symbol', 'Unknown')}: {e}"
                )
                continue

        # Add explanatory information
        message += (
            "<i>• 🏆 <b>Final Score (0–100)</b>: Average of Technical and Fundamental scores (more is better).</i>\n"
            "<i>• 📈 <b>Technical Score (0–100)</b>: Evaluates stock movement using Stock Statistical Analysis.</i>\n"
            "<i>• 💼 <b>Fundamental Score (0–100)</b>: Assesses company health using Company Fundamentals.</i>\n"
        )

        return message
    except Exception as e:
        log_error(f"❌ Error composing message: {e}")
        raise


def send_telegram_message(bot_token: str, chat_id: str, text: str) -> None:
    """
    Sends a Telegram message using the Bot API.

    Args:
        bot_token (str): Telegram bot token.
        chat_id (str): Telegram chat ID.
        text (str): The message text to send.

    Returns:
        None
    """
    try:
        bot = Bot(token=bot_token)
        bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML")
        log_success("📤 Telegram alert sent successfully.")
    except Exception as e:
        log_error(f"❌ Failed to send Telegram message: {e}")
