__author__ = "Adnan Karol"
__version__ = "1.0.0"
__maintainer__ = "Adnan Karol"
__email__ = "adnanmushtaq5@gmail.com"
__status__ = "DEV"

# Import Dependencies
import yfinance as yf
import numpy as np
import pandas as pd
from typing import Any, Dict, Optional
from src.utils.logger import log_info, log_warn, log_error
from utils.indicators import sma, rsi, clamp


def extract_scalar(series: pd.Series) -> Optional[float]:
    """
    Extracts the last scalar value from a pandas Series.

    Args:
        series (pd.Series): The pandas Series to extract the value from.

    Returns:
        Optional[float]: The last scalar value as a float, or None if the Series is empty.
    """
    if not series.empty:
        val = series.iloc[-1]
        if isinstance(val, pd.Series):
            val = val.item()
        return float(val)
    return None


def compute_scores_for_ticker(
    ticker: str, cfg: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """
    Computes technical and fundamental scores for a given stock ticker.

    Args:
        ticker (str): The stock ticker symbol.
        cfg (Dict[str, Any]): Configuration dictionary containing scoring parameters.

    Returns:
        Optional[Dict[str, Any]]: A dictionary containing scores and stock metrics, or None if scoring fails.
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
            auto_adjust=False,
        )

        if df is None or df.empty or len(df) < 30:
            log_warn(f"No sufficient data for {ytick}")
            return None

        df = df.dropna()
        close = df["Close"]
        vol = df["Volume"]

        sma_period = int(cfg["scoring"].get("sma_period", 20))
        rsi_period = int(cfg["scoring"].get("rsi_period", 14))
        vol_period = int(cfg["scoring"].get("vol_period", 30))

        sma20_series = sma(close, sma_period)
        if sma20_series.empty or len(sma20_series) < sma_period:
            log_warn(f"SMA calculation failed for {ytick} due to insufficient data.")
            return None
        sma20 = extract_scalar(sma20_series)
        if sma20 is None:
            log_warn(f"Insufficient data for SMA for {ytick}")
            return None

        last_close = extract_scalar(close)
        if last_close is None:
            log_warn(f"Insufficient data for last close for {ytick}")
            return None

        sma_signal = 1 if last_close > sma20 else -1

        rsi14_series = rsi(close, rsi_period)
        if rsi14_series.empty or len(rsi14_series) < rsi_period:
            log_warn(f"RSI calculation failed for {ytick} due to insufficient data.")
            return None
        rsi14 = extract_scalar(rsi14_series)
        if rsi14 is None:
            log_warn(f"Insufficient data for RSI for {ytick}")
            return None

        rsi_signal = 1 if rsi14 < 30 else (-1 if rsi14 > 70 else 0)

        vol30_series = vol.rolling(vol_period).mean()
        if vol30_series.empty or len(vol30_series) < vol_period:
            log_warn(f"Volume calculation failed for {ytick} due to insufficient data.")
            return None
        vol30 = extract_scalar(vol30_series)
        if vol30 is None:
            log_warn(f"Insufficient data for volume for {ytick}")
            return None

        vol_signal = 1 if extract_scalar(vol.iloc[-1:]) > 2 * vol30 else 0

        w = cfg["scoring"].get("weights", {})
        tech_raw = (
            w.get("momentum", 0) * sma_signal
            + w.get("rsi", 0) * rsi_signal
            + w.get("volume", 0) * vol_signal
        )
        max_raw = w.get("momentum", 0) + w.get("rsi", 0) + w.get("volume", 0)
        tech_score = clamp((tech_raw / max_raw) * 100) if max_raw > 0 else 0

        fund_score = 0
        pe = None
        try:
            t = yf.Ticker(ytick)
            info = t.info or {}
            pe = info.get("trailingPE", None)

            q_fin = t.quarterly_financials
            if q_fin is not None and not q_fin.empty:
                rev_now = rev_prev = net_now = net_prev = None

                for k in ["Total Revenue", "Revenue", "TotalRevenue"]:
                    if k in q_fin.index and q_fin.loc[k].shape[0] >= 2:
                        rev_now = float(q_fin.loc[k].iloc[0])
                        rev_prev = float(q_fin.loc[k].iloc[1])
                        break

                for k in ["Net Income", "NetIncome"]:
                    if k in q_fin.index and q_fin.loc[k].shape[0] >= 2:
                        net_now = float(q_fin.loc[k].iloc[0])
                        net_prev = float(q_fin.loc[k].iloc[1])
                        break

                if rev_now is not None and rev_prev is not None and rev_prev != 0:
                    rev_g = (rev_now - rev_prev) / abs(rev_prev)
                    fund_score += 50 * np.tanh(rev_g)

                if net_now is not None and net_prev is not None and net_prev != 0:
                    net_g = (net_now - net_prev) / abs(net_prev)
                    fund_score += 50 * np.tanh(net_g)

            if isinstance(pe, (int, float)) and pe > 0:
                if pe < 20:
                    fund_score += 10
                elif pe > 60:
                    fund_score -= 10
        except Exception as fe:
            log_warn(f"Fundamentals unavailable for {ytick}: {fe}")

        fund_score = clamp(fund_score)

        last_price = extract_scalar(close)
        low_1m, high_1m = (
            float(close.tail(22).min().iloc[0]) if len(close) >= 22 else None,
            float(close.tail(22).max().iloc[0]) if len(close) >= 22 else None,
        )
        low_3m, high_3m = (
            float(close.tail(66).min().iloc[0]) if len(close) >= 66 else None,
            float(close.tail(66).max().iloc[0]) if len(close) >= 66 else None,
        )

        fund_w = w.get("fundamentals", 0)
        tech_w = w.get("momentum", 0) + w.get("rsi", 0) + w.get("volume", 0)
        total_w = tech_w + fund_w
        final_score = (
            clamp(tech_score * (tech_w / total_w) + fund_score * (fund_w / total_w))
            if total_w > 0
            else tech_score
        )

        return {
            "symbol": ticker,
            "yf_symbol": ytick,
            "tech_score": int(tech_score),
            "fund_score": int(fund_score),
            "final_score": int(final_score),
            "last_close": last_price,
            "rsi": rsi14,
            "sma20": sma20,
            "volume": int(vol.iloc[-1].iloc[0]) if not vol.empty else None,
            "vol30": int(vol30),
            "pe": pe if isinstance(pe, (int, float)) else None,
            "low_1m": low_1m,
            "high_1m": high_1m,
            "low_3m": low_3m,
            "high_3m": high_3m,
        }
    except yf.YFPricesMissingError as e:
        log_warn(f"⚠️ YFPricesMissingError for {ticker}: {e}")
        return None

    except ValueError as e:
        log_warn(f"⚠️ ValueError for {ticker}: {e}")
        return None

    except Exception as e:
        log_error(f"❌ Unexpected error for {ticker}: {type(e).__name__}: {e}")
        return None
