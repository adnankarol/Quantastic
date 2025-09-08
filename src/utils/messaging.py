__author__ = "Adnan Karol"
__version__ = "1.0.0"
__maintainer__ = "Adnan Karol"
__email__ = "adnanmushtaq5@gmail.com"
__status__ = "DEV"

from typing import Any, Dict, List
from telegram import Bot
from src.utils.logger import log_success, log_error
from datetime import datetime
import pandas as pd
import html  # For escaping HTML content


def compose_message(results: list, cfg: dict, skipped_symbols: list = None) -> str:
    """
    Composes a Telegram message summarizing the stock analysis results.

    Args:
        results (list): List of dictionaries containing stock analysis results.
        cfg (dict): Configuration dictionary.
        skipped_symbols (list): List of skipped symbols with reasons.

    Returns:
        str: HTML-formatted message for Telegram.
    """
    try:
        top_n_watch = cfg["scoring"].get("top_n_watch", 5)
        top_n_avoid = cfg["scoring"].get("top_n_avoid", 3)

        # Read thresholds from config
        buy_threshold = cfg["thresholds"].get("buy_threshold", 70)
        avoid_threshold = cfg["thresholds"].get("avoid_threshold", 39)

        # Categorize stocks
        watchlist = [
            stock for stock in results if stock["final_score"] >= buy_threshold
        ]
        avoidlist = [
            stock for stock in results if stock["final_score"] <= avoid_threshold
        ]

        # Sort watchlist and avoidlist
        watchlist = sorted(watchlist, key=lambda x: x["final_score"], reverse=True)[
            :top_n_watch
        ]
        avoidlist = sorted(avoidlist, key=lambda x: x["final_score"])[:top_n_avoid]

        message = "<b>🚀 Quantastic — Market Open Alert</b>\n"
        message += f"📊 Scanned <b>{len(results)}</b> stocks.\n\n"

        # Watchlist Section
        if watchlist:
            message += f"Showing top <b>{len(watchlist)}</b> picks:\n\n"
            message += "<b>🔥 Watchlist (Potential Buys)</b>\n"
            for stock in watchlist:
                message += (
                    f"🏷️ <b>{stock['symbol']}</b>\n"
                    f"📊 Final Score: <b>{stock['final_score']}</b> (Tech: {stock['tech_score']}, Fund: {stock['fund_score']})\n"
                    f"💰 Last Price: ₹{stock['last_close']:.2f}\n"
                    f"✅ Recommendation: 🟢 <b>Buy</b>\n\n"
                )
        else:
            message += "⚠️ No stocks met the criteria for the Watchlist today.\n\n"

        # Avoid List Section
        if avoidlist:
            message += "---\n\n"
            message += "<b>⚠️ Avoid List</b>\n"
            for stock in avoidlist:
                message += (
                    f"🏷️ <b>{stock['symbol']}</b>\n"
                    f"📊 Final Score: <b>{stock['final_score']}</b> (Tech: {stock['tech_score']}, Fund: {stock['fund_score']})\n"
                    f"💰 Last Price: ₹{stock['last_close']:.2f}\n"
                    f"❌ Recommendation: 🔴 <b>Avoid</b>\n\n"
                )
        else:
            message += (
                "---\n\n⚠️ No stocks met the criteria for the Avoid List today.\n\n"
            )

        # Skipped Symbols Section
        if skipped_symbols:
            message += "---\n\n"
            message += "<b>⚠️ Skipped Symbols</b>\n"
            for symbol in skipped_symbols:
                message += f"🏷️ <b>{symbol}</b>\n"
            message += "\n"

        # Add informational section at the end
        message += "---\n\n"
        message += "<i>ℹ️ <b>Score Ranges and Explanation</b></i>\n"
        message += (
            "<i>• <b>Technical Score (0–100)</b>: Evaluates stock movement using SMA, RSI, Volume, MACD, etc.</i>\n"
            "<i>• <b>Fundamental Score (0–100)</b>: Assesses company health using PE ratio, ROE, Revenue Growth, etc.</i>\n"
            "<i>• <b>Final Score (0–100)</b>: Average of Technical and Fundamental scores.</i>\n"
            "<i>• <b>High Score (70–100)</b>: Strong Buy/Watch.</i>\n"
            "<i>• <b>Medium Score (40–69)</b>: Hold/Neutral.</i>\n"
            "<i>• <b>Low Score (0–39)</b>: Avoid/Sell.</i>\n"
        )

        return message.strip()
    except Exception as e:
        log_error(f"❌ Error composing message: {e}")
        return "❌ Error generating message."


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
