import pytest
from src.utils.scoring import (
    compute_macd,
    compute_bollinger_bands,
    compute_scores_for_ticker,
)
import pandas as pd


def test_compute_scores_for_ticker():
    # Mock configuration and input
    mock_config = {
        "weights": {"technical": 0.6, "fundamental": 0.4},
        "technical": {"sma_period": 20, "rsi_period": 14},
    }
    mock_symbol = "RELIANCE"

    # Call the function
    result = compute_scores_for_ticker(mock_symbol, mock_config)

    # Assertions
    assert isinstance(result, dict), "Result should be a dictionary"
    assert "symbol" in result, "Result should contain 'symbol'"
    assert "score" in result, "Result should contain 'score'"
    assert -100 <= result["score"] <= 100, "Score should be between -100 and 100"


def test_compute_macd():
    # Mock data
    data = pd.DataFrame({"Close": [100, 102, 104, 103, 105, 107, 110]})
    mock_config = {
        "scoring": {
            "macd_fast_period": 3,
            "macd_slow_period": 6,
            "macd_signal_period": 2,
        }
    }

    # Call the function
    score = compute_macd(data, mock_config)

    # Assertions
    assert 0 <= score <= 100, "MACD score should be between 0 and 100"


def test_compute_bollinger_bands():
    # Mock data
    data = pd.DataFrame({"Close": [100, 102, 104, 103, 105, 107, 110]})
    mock_config = {"scoring": {"bollinger_period": 3, "bollinger_std_dev": 2}}

    # Call the function
    score = compute_bollinger_bands(data, mock_config)

    # Assertions
    assert 0 <= score <= 100, "Bollinger Bands score should be between 0 and 100"
