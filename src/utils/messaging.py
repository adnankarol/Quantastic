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


def compose_message(results: List[Dict[str, Any]], cfg: Dict[str, Any]) -> str:
    """
    Composes a Telegram message summarizing stock scores and recommendations.

    Args:
        results (List[Dict[str, Any]]): List of stock scoring results.
        cfg (Dict[str, Any]): Configuration dictionary.

    Returns:
        str: The formatted Telegram message as an HTML string.
    """
    now = datetime.now().strftime("%d %b %Y, %H:%M IST")

    if not results:
        return f"<b>🚀 Quantastic — {now}</b>\n⚠️ No data available today."

    df = pd.DataFrame(results).dropna(subset=["final_score"])
    if df.empty:
        return f"<b>🚀 Quantastic — {now}</b>\n⚠️ No valid scores today."

    df = df.sort_values("final_score", ascending=False)
    topn = int(cfg["scoring"]["top_n_watch"])
    top_watch = df.head(topn)

    lines = [
        f"<b>🚀 Quantastic — Market Open Alert</b> ({now})",
        f"📊 Scanned <b>{len(df)}</b> stocks. Showing top <b>{min(topn, len(df))}</b> picks:\n",
        "<b>🔥 Watchlist (Potential Buys)</b>",
    ]

    for _, r in top_watch.iterrows():
        symbol = html.escape(str(r.get("symbol", "")))
        final_score = html.escape(str(int(r.get("final_score", 0))))
        tech_score = html.escape(str(int(r.get("tech_score", 0))))
        fund_score = html.escape(str(int(r.get("fund_score", 0))))
        last_close = html.escape(f"{r.get('last_close', 0):.2f}")
        low_1m = html.escape(f"{r.get('low_1m', 0):.2f}")
        high_1m = html.escape(f"{r.get('high_1m', 0):.2f}")
        low_3m = html.escape(f"{r.get('low_3m', 0):.2f}")
        high_3m = html.escape(f"{r.get('high_3m', 0):.2f}")
        rsi = html.escape(f"{r.get('rsi', 0):.1f}")

        pe_txt = ""
        if isinstance(r.get("pe"), (int, float)):
            pe_formatted = f"{r['pe']:.1f}"
            pe_txt = f" | PE: {html.escape(pe_formatted)}"

        recommendation = (
            "🟢 <b>Buy</b>"
            if r.get("final_score", 0) > 50
            else "🟡 <b>Hold</b>" if r.get("final_score", 0) > 0 else "🔴 <b>Avoid</b>"
        )

        lines.append(
            f"🏷️ {symbol} — <b>{final_score}</b> "
            f"(Tech: {tech_score}, Fund: {fund_score})\n"
            f"💰 Last Price: ₹{last_close}\n"
            f"📉 1M Range: ₹{low_1m} → ₹{high_1m}\n"
            f"📈 3M Range: ₹{low_3m} → ₹{high_3m}\n"
            f"📊 RSI: {rsi}{pe_txt}\n"
            f"✅ Recommendation: {recommendation}\n"
        )

    lines.append(
        "\n<b>ℹ️ Quantastic Score:</b> Our proprietary score ranges from -100 to +100. "
        "It combines technical indicators (SMA, RSI, Volume) and fundamentals (Revenue, Net Income, PE). "
        "Higher scores indicate stronger buy signals.\n"
        "<i>Quantastic Score blends simple technicals (SMA/RSI/Volume) "
        "with fundamentals (Revenue & Net Income growth, PE). Educational use only.</i>"
    )
    return "\n".join(lines)


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
