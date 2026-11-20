from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from app.clients.events_provider import EventsProviderClient
from app.config import get_settings


@pytest.fixture
def client(monkeypatch):
    """Клиент с подменёнными настройками (URL и ключ)."""
    get_settings.cache_clear()
    monkeypatch.setenv("EVENTS_PROVIDER_URL", "http://events-provider.test")
    monkeypatch.setenv("EVENTS_PROVIDER_API_KEY", "test-api-key")

    c = EventsProviderClient()
    yield c
    get_settings.cache_clear()


def _mock_response(json_data, status_code=200):
    response = MagicMock(spec=httpx.Response)
    response.status_code = status_code
    response.json.return_value = json_data
    response.raise_for_status = MagicMock()
    return response


@pytest.mark.asyncio
async def test_get_events_first_page(client):
    fake = {"next": "http://next", "previous": None, "results": [{"id": "1"}]}
    response = _mock_response(fake)

    with patch("httpx.AsyncClient.get", new=AsyncMock(return_value=response)) as mock_get:
        result = await client.get_events(changed_at="2000-01-01")

    assert result == fake
    mock_get.assert_awaited_once()
    _, kwargs = mock_get.call_args
    assert kwargs["headers"]["x-api-key"] == "test-api-key"
    assert kwargs["params"] == {"changed_at": "2000-01-01"}
    assert mock_get.call_args.args[0] == "http://events-provider.test/api/events/"
    response.raise_for_status.assert_called_once()


@pytest.mark.asyncio
async def test_get_events_with_cursor_uses_full_url(client):
    fake = {"next": None, "previous": None, "results": []}
    response = _mock_response(fake)
    next_url = "http://events-provider.test/api/events/?changed_at=2000-01-01&cursor=abc"

    with patch("httpx.AsyncClient.get", new=AsyncMock(return_value=response)) as mock_get:
        await client.get_events(cursor=next_url)

    _, kwargs = mock_get.call_args
    assert mock_get.call_args.args[0] == next_url
    assert kwargs["params"] is None


@pytest.mark.asyncio
async def test_get_seats_calls_correct_url(client):
    fake = {"seats": ["A1", "A2"]}
    response = _mock_response(fake)

    with patch("httpx.AsyncClient.get", new=AsyncMock(return_value=response)) as mock_get:
        result = await client.get_seats("event-123")

    assert result == fake
    assert mock_get.call_args.args[0] == "http://events-provider.test/api/events/event-123/seats/"


@pytest.mark.asyncio
async def test_register_posts_payload(client):
    fake = {"ticket_id": "ticket-uuid"}
    response = _mock_response(fake, status_code=201)

    with patch("httpx.AsyncClient.post", new=AsyncMock(return_value=response)) as mock_post:
        result = await client.register(
            event_id="event-1",
            first_name="Иван",
            last_name="Иванов",
            email="ivan@example.com",
            seat="A15",
        )

    assert result == fake
    assert mock_post.call_args.args[0] == "http://events-provider.test/api/events/event-1/register/"
    assert mock_post.call_args.kwargs["json"] == {
        "first_name": "Иван",
        "last_name": "Иванов",
        "email": "ivan@example.com",
        "seat": "A15",
    }


@pytest.mark.asyncio
async def test_unregister_sends_delete(client):
    fake = {"success": True}
    response = _mock_response(fake)

    with patch("httpx.AsyncClient.request", new=AsyncMock(return_value=response)) as mock_request:
        result = await client.unregister(event_id="event-1", ticket_id="ticket-1")

    assert result == fake
    args, kwargs = mock_request.call_args
    assert args[0] == "DELETE"
    assert args[1] == "http://events-provider.test/api/events/event-1/unregister/"
    assert kwargs["json"] == {"ticket_id": "ticket-1"}
