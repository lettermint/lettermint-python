"""Pytest configuration and fixtures."""

import pytest


@pytest.fixture
def api_token() -> str:
    """Provide a test API token."""
    return "test-api-token"


@pytest.fixture
def webhook_secret() -> str:
    """Provide a test webhook secret."""
    return "test-webhook-secret"
