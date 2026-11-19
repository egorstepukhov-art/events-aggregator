import pytest


@pytest.fixture
def api_key() -> str:
    return "test-api-key"


@pytest.fixture
def base_url() -> str:
    return "http://events-provider.test"