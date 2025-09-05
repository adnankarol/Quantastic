import pytest


@pytest.fixture
def mock_config():
    return {
        "weights": {"technical": 0.6, "fundamental": 0.4},
        "technical": {"sma_period": 20, "rsi_period": 14},
    }


@pytest.fixture
def mock_credentials():
    return {
        "telegram": {
            "bot_token": "mock_bot_token",
            "chat_ids": ["123456789", "987654321"],
        }
    }
