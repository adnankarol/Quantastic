__author__ = "Adnan Karol"
__version__ = "1.0.0"
__maintainer__ = "Adnan Karol"
__email__ = "adnanmushtaq5@gmail.com"
__status__ = "DEV"

# Import Dependencies
import numpy as np
import pandas as pd


def sma(series: pd.Series, period: int) -> pd.Series:
    """
    Calculates the Simple Moving Average (SMA) for a given series.

    Args:
        series (pd.Series): The input series (e.g., stock prices).
        period (int): The period over which to calculate the SMA.

    Returns:
        pd.Series: A series containing the SMA values.
    """
    return series.rolling(window=period).mean()


def rsi(series: pd.Series, period: int) -> pd.Series:
    """
    Calculates the Relative Strength Index (RSI) for a given series.

    Args:
        series (pd.Series): The input series (e.g., stock prices).
        period (int): The period over which to calculate the RSI.

    Returns:
        pd.Series: A series containing the RSI values.
    """
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))


def clamp(value: float, min_value: float = -100, max_value: float = 100) -> float:
    """
    Clamps a value between a minimum and maximum range.

    Args:
        value (float): The value to clamp.
        min_value (float): The minimum allowable value (default: -100).
        max_value (float): The maximum allowable value (default: 100).

    Returns:
        float: The clamped value.
    """
    return max(min_value, min(value, max_value))
