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


def compute_fundamental_score(data: dict) -> int:
    """
    Computes the fundamental score for a stock.

    Args:
        data (dict): Fundamental data for the stock.

    Returns:
        int: The fundamental score.
    """
    try:
        if data is None:
            log_warn("⚠️ Fundamental data is None. Skipping calculation.")
            return 0

        # Ensure data is iterable
        if not isinstance(data, dict):
            log_error("❌ Fundamental data is not a dictionary. Skipping calculation.")
            return 0

        # ...existing fundamental score calculation logic...
    except Exception as e:
        log_error(f"❌ Fundamental calculation failed: {e}")
        return 0


# -----------------------------
# Main Scoring Function
# -----------------------------
def compute_scores_for_ticker(
    ticker: str, cfg: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """
    Computes technical and fundamental scores for a given stock ticker.

    Args:
        ticker (str): Stock ticker symbol.
        cfg (Dict[str, Any]): Configuration dictionary containing scoring parameters.

    Returns:
        Optional[Dict[str, Any]]: Dictionary containing scores and stock metrics, or None if scoring fails.
    """
    try:
        suffix = cfg["universe"].get("suffix", "")
        ytick = (
            ticker
            if ticker.endswith((".NS", ".BO")) or not suffix
            else f"{ticker}{suffix}"
        )

        df = yf.download(
            ytick,
            period="6mo",
            interval="1d",
            progress=False,
            threads=False,
            auto_adjust=False,  # Explicitly set auto_adjust to False
        )

        if df is None or df.empty or len(df) < 30:
            log_warn(f"No sufficient data for {ytick}")
            return None
        df = df.dropna()
        close = df["Close"]
        vol = df["Volume"]

        # Technical metrics
        sma_period = int(cfg["scoring"].get("sma_period", 20))
        rsi_period = int(cfg["scoring"].get("rsi_period", 14))
        vol_period = int(cfg["scoring"].get("vol_period", 30))

        sma20 = extract_scalar(sma(close, sma_period))
        if sma20 is None:
            return None
        last_close = extract_scalar(close)
        sma_signal = 1 if last_close > sma20 else 0

        rsi_val = extract_scalar(rsi(close, rsi_period))
        rsi_signal = 1 - (rsi_val / 100) if rsi_val is not None else 0

        vol_avg = extract_scalar(vol.rolling(vol_period).mean())
        vol_signal = normalize_0_1(
            extract_scalar(vol) if vol_avg else 0, vol_avg * 0.5, vol_avg * 2
        )

        macd_signal = compute_macd(df, cfg)

        # Weighted technical score
        w = cfg["scoring"].get("weights", {})
        tech_components = [
            (sma_signal, w.get("sma", 0)),
            (rsi_signal, w.get("rsi", 0)),
            (vol_signal, w.get("volume", 0)),
            (macd_signal, w.get("macd", 0)),
        ]
        tech_score = (
            np.average(
                [v for v, _ in tech_components],
                weights=[wt for _, wt in tech_components],
            )
            if sum([wt for _, wt in tech_components]) > 0
            else 0
        )

        # Fundamental score
        fund_score = compute_fundamentals(ytick)

        # Composite final score
        final_score = clamp(np.mean([tech_score, fund_score]))

        return {
            "symbol": ticker,
            "yf_symbol": ytick,
            "tech_score": round(tech_score * 100),
            "fund_score": round(fund_score * 100),
            "final_score": round(final_score * 100),
            "last_close": last_close,
            "rsi": rsi_val,
            "sma20": sma20,
            "macd": macd_signal,
        }
    except Exception as e:
        log_error(f"❌ Unexpected error for {ticker}: {type(e).__name__}: {e}")
        return None
