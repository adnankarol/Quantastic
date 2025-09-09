__author__ = "Adnan Karol"
__version__ = "1.1.0"
__maintainer__ = "Adnan Karol"
__email__ = "adnanmushtaq5@gmail.com"
__status__ = "DEV"

import yfinance as yf
import numpy as np
import pandas as pd
from typing import Any, Dict, Optional
from src.utils.logger import log_info, log_warn, log_error
from utils.indicators import sma, rsi, clamp
from yfinance import Ticker  # Import the Ticker class


# -----------------------------
# Helper Functions
# -----------------------------
def extract_scalar(series: pd.Series) -> Optional[float]:
    try:
        if series.empty:
            return None
        val = series.iloc[-1]
        if isinstance(val, (pd.Series, np.ndarray)) and len(val) == 1:
            return float(val.item())
        elif isinstance(val, (int, float)):
            return float(val)
        else:
            return None
    except Exception as e:
        log_error(f"Error extracting scalar value: {e}")
        return None


def normalize_0_1(value: float, min_value: float, max_value: float) -> float:
    try:
        return (
            max(0, min(1, (value - min_value) / (max_value - min_value)))
            if max_value > min_value
            else 0
        )
    except Exception as e:
        log_error(f"Error normalizing value: {e}")
        return 0


# -----------------------------
# MACD Indicator
# -----------------------------
def compute_macd(data: pd.DataFrame, cfg: dict) -> float:
    try:
        fast, slow, signal = (
            cfg["scoring"].get("macd_fast_period", 12),
            cfg["scoring"].get("macd_slow_period", 26),
            cfg["scoring"].get("macd_signal_period", 9),
        )
        data["EMA_fast"] = data["Close"].ewm(span=fast, adjust=False).mean()
        data["EMA_slow"] = data["Close"].ewm(span=slow, adjust=False).mean()
        data["MACD"] = data["EMA_fast"] - data["EMA_slow"]
        data["Signal"] = data["MACD"].ewm(span=signal, adjust=False).mean()
        return 1 if data["MACD"].iloc[-1] > data["Signal"].iloc[-1] else 0
    except Exception as e:
        log_error(f"Error computing MACD: {e}")
        return 0


# -----------------------------
# Fundamental Score
# -----------------------------
def compute_fundamentals(ticker: str) -> float:
    """
    Computes the fundamental score for a stock.

    Args:
        ticker (str): Stock ticker symbol.

    Returns:
        float: The fundamental score.
    """
    try:
        t = yf.Ticker(ticker)
        info = t.info or {}
        pe = info.get("trailingPE", 50)
        roe = info.get("returnOnEquity", 0.15)
        debt_eq = info.get("debtToEquity", 0.5)

        # Normalize metrics 0–1
        pe_score = 1 if pe < 25 else (0 if pe > 60 else 0.5)
        roe_score = normalize_0_1(roe, 0, 0.3)
        debt_score = 1 - normalize_0_1(debt_eq, 0, 2)

        # Revenue/Net income growth (latest two quarters)
        q_fin = t.quarterly_financials
        rev_score = net_score = 0
        if q_fin is not None and not q_fin.empty:
            rev_series = next(
                (
                    q_fin.loc[k]
                    for k in ["Total Revenue", "Revenue", "TotalRevenue"]
                    if k in q_fin.index
                ),
                None,
            )
            net_series = next(
                (q_fin.loc[k] for k in ["Net Income", "NetIncome"] if k in q_fin.index),
                None,
            )
            if rev_series is not None and len(rev_series) >= 2:
                rev_score = np.tanh(
                    (rev_series.iloc[0] - rev_series.iloc[1]) / abs(rev_series.iloc[1])
                )
            if net_series is not None and len(net_series) >= 2:
                net_score = np.tanh(
                    (net_series.iloc[0] - net_series.iloc[1]) / abs(net_series.iloc[1])
                )

        fund_score = np.mean([pe_score, roe_score, debt_score, rev_score, net_score])
        return clamp(fund_score)
    except Exception as e:
        log_warn(f"Fundamental calculation failed for {ticker}: {e}")
        return 0


def compute_fundamental_score(ticker: Ticker, cfg: dict) -> float:
    """
    Computes the fundamental score for a stock.

    Args:
        ticker (Ticker): The Ticker object for the stock.
        cfg (dict): Configuration dictionary.

    Returns:
        float: The fundamental score (0–100).
    """
    try:
        info = ticker.info or {}
        pe = info.get("trailingPE", 50)
        roe = info.get("returnOnEquity", 0.15)
        debt_eq = info.get("debtToEquity", 0.5)

        # Normalize metrics 0–1
        pe_score = 1 if pe < 25 else (0 if pe > 60 else 0.5)
        roe_score = normalize_0_1(roe, 0, 0.3)
        debt_score = 1 - normalize_0_1(debt_eq, 0, 2)

        # Revenue/Net income growth (latest two quarters)
        q_fin = ticker.quarterly_financials
        rev_score = net_score = 0
        if q_fin is not None and not q_fin.empty:
            rev_series = next(
                (
                    q_fin.loc[k]
                    for k in ["Total Revenue", "Revenue", "TotalRevenue"]
                    if k in q_fin.index
                ),
                None,
            )
            net_series = next(
                (q_fin.loc[k] for k in ["Net Income", "NetIncome"] if k in q_fin.index),
                None,
            )
            if rev_series is not None and len(rev_series) >= 2:
                rev_score = np.tanh(
                    (rev_series.iloc[0] - rev_series.iloc[1]) / abs(rev_series.iloc[1])
                )
            if net_series is not None and len(net_series) >= 2:
                net_score = np.tanh(
                    (net_series.iloc[0] - net_series.iloc[1]) / abs(net_series.iloc[1])
                )

        # Combine scores into a final fundamental score
        fund_score = np.mean([pe_score, roe_score, debt_score, rev_score, net_score])
        return round(clamp(fund_score) * 100, 2)  # Scale to 0–100
    except Exception as e:
        log_warn(f"⚠️ Fundamental calculation failed for {ticker.ticker}: {e}")
        return 0


# -----------------------------
# Technical Score
# -----------------------------
def compute_technical_score(data: pd.DataFrame, cfg: dict) -> float:
    """
    Computes the technical score for a stock based on various indicators.

    Args:
        data (pd.DataFrame): Historical stock data.
        cfg (dict): Configuration dictionary.

    Returns:
        float: The technical score (0–100).
    """
    try:
        # Compute SMA signal
        sma_period = cfg["scoring"].get("sma_period", 20)
        sma_signal = sma(data["Close"], sma_period)
        sma_score = 1 if data["Close"].iloc[-1] > sma_signal.iloc[-1] else 0

        # Compute RSI signal
        rsi_period = cfg["scoring"].get("rsi_period", 14)
        rsi_signal = rsi(data["Close"], rsi_period)
        rsi_score = 1 if 30 < rsi_signal.iloc[-1] < 70 else 0

        # Compute MACD signal
        macd_score = compute_macd(data, cfg)

        # Combine scores using weights
        weights = cfg["scoring"]["weights"]
        tech_score = (
            weights["momentum"] * sma_score
            + weights["rsi"] * rsi_score
            + weights["macd"] * macd_score
        ) / sum(weights.values())

        return round(tech_score * 100, 2)  # Scale to 0–100
    except Exception as e:
        log_warn(f"⚠️ Technical calculation failed: {e}")
        return 0


# -----------------------------
# Main Scoring Function
# -----------------------------
def compute_scores_for_ticker(symbol: str, cfg: dict) -> dict:
    """
    Computes technical and fundamental scores for a given stock symbol.

    Args:
        symbol (str): The stock symbol to compute scores for.
        cfg (dict): Configuration dictionary.

    Returns:
        dict: A dictionary containing the computed scores, last close, and average price.
    """
    try:
        # Fetch data for the symbol
        ticker = Ticker(f"{symbol}.NS")
        data = ticker.history(period="6mo")

        if data is None or data.empty:
            raise ValueError(f"No data available for {symbol}")

        # Compute technical and fundamental scores
        tech_score = compute_technical_score(data, cfg)
        fund_score = compute_fundamental_score(ticker, cfg)

        if tech_score is None or fund_score is None:
            raise ValueError(f"Failed to compute scores for {symbol}")

        # Calculate last close price
        last_close = data["Close"].iloc[-1] if "Close" in data.columns else None

        # Calculate average price over the configured duration
        avg_price_duration = cfg["scoring"].get("avg_price_duration", 30)
        avg_price = (
            data["Close"].iloc[-avg_price_duration:].mean()
            if len(data["Close"]) >= avg_price_duration
            else None
        )

        # Combine scores into a final score
        final_score = (tech_score + fund_score) / 2
        return {
            "symbol": symbol,
            "tech_score": tech_score,
            "fund_score": fund_score,
            "final_score": final_score,
            "last_close": round(last_close, 2) if last_close else "N/A",
            "avg_price": round(avg_price, 2) if avg_price else "N/A",
        }
    except Exception as e:
        log_warn(f"⚠️ Fundamental calculation failed for {symbol}: {e}")
        return None
