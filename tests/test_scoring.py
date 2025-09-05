import pytest
from src.utils.scoring import compute_scores_for_ticker  # Updated import path


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
