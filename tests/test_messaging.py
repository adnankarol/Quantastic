import pytest
from utils.messaging import compose_message


def test_compose_message():
    # Mock data
    mock_results = [
        {"symbol": "RELIANCE", "score": 78, "technical": 80, "fundamental": 75},
        {"symbol": "TCS", "score": 65, "technical": 70, "fundamental": 60},
    ]
    mock_config = {"universe": {"top_picks": 5}}

    # Call the function
    message = compose_message(mock_results, mock_config)

    # Assertions
    assert isinstance(message, str), "Message should be a string"
    assert "<b>🚀 Quantastic" in message, "Message should contain header"
    assert "RELIANCE" in message, "Message should include stock symbols"
