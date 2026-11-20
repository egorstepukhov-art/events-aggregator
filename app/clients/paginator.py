from typing import Any

from app.clients.events_provider import EventsProviderClient


class EventsPaginator:
    """
    Асинхронный итератор для обхода всех страниц Events Provider API.
    """

    def __init__(self, client: EventsProviderClient, changed_at: str = "2000-01-01"):
        self.client = client
        self.changed_at = changed_at
        self._next_url: str | None = None
        self._started = False

    def __aiter__(self) -> "EventsPaginator":
        return self

    async def __anext__(self) -> list[dict[str, Any]]:
        if not self._started:
            # Первый запрос
            data = await self.client.get_events(changed_at=self.changed_at)
            self._started = True
        else:
            if not self._next_url:
                raise StopAsyncIteration
            data = await self.client.get_events(cursor=self._next_url)

        self._next_url = data.get("next")
        results = data.get("results", [])

        if not results and not self._next_url:
            raise StopAsyncIteration

        return results
