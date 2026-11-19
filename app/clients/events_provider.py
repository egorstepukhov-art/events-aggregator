from typing import Any

import httpx

from app.config import get_settings


class EventsProviderClient:
    def __init__(self):
        settings = get_settings()
        self.base_url = settings.events_provider_url.rstrip("/")
        self.api_key = settings.events_provider_api_key
        self.headers = {
            "x-api-key": self.api_key,
            "Accept": "application/json",
        }

    async def get_events(self, changed_at: str = "2000-01-01", cursor: str | None = None) -> dict[str, Any]:
        """Получение списка событий с cursor-based пагинацией."""
        if cursor:
            url = cursor
            params = None
        else:
            url = f"{self.base_url}/api/events/"
            params = {"changed_at": changed_at}

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()

    async def get_seats(self, event_id: str) -> dict[str, Any]:
        """Получение свободных мест на мероприятии."""
        url = f"{self.base_url}/api/events/{event_id}/seats/"
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()

    async def register(
        self,
        event_id: str,
        first_name: str,
        last_name: str,
        email: str,
        seat: str,
    ) -> dict[str, Any]:
        """Регистрация на мероприятие."""
        url = f"{self.base_url}/api/events/{event_id}/register/"
        payload = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "seat": seat,
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()

    async def unregister(self, event_id: str, ticket_id: str) -> dict[str, Any]:
        """Отмена регистрации."""
        url = f"{self.base_url}/api/events/{event_id}/unregister/"
        payload = {"ticket_id": ticket_id}
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.request("DELETE", url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()