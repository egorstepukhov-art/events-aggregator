from uuid import UUID

from app.models import Event
from app.repositories.events import EventRepository
from app.services.cache import TTLCache
from app.services.protocols import EventsProviderClientProtocol


class EventNotFound(Exception):
    pass


class EventUnexpectedStatus(Exception):
    pass


# Кэш мест на 30 секунд (по требованию задания)
_seats_cache: TTLCache[list[str]] = TTLCache(ttl_seconds=30)


class GetEventsUsecase:
    def __init__(self, events: EventRepository):
        self.events = events

    async def do(self, *, date_from: str | None, page: int, page_size: int):
        return await self.events.list(
            date_from=date_from, page=page, page_size=page_size
        )


class GetEventUsecase:
    def __init__(self, events: EventRepository):
        self.events = events

    async def do(self, event_id: UUID) -> Event:
        event = await self.events.get(event_id)
        if not event:
            raise EventNotFound
        return event


class GetSeatsUsecase:
    def __init__(self, events: EventRepository, client: EventsProviderClientProtocol):
        self.events = events
        self.client = client

    async def do(self, event_id: UUID) -> list[str]:
        event = await self.events.get(event_id)
        if not event:
            raise EventNotFound
        if event.status != "published":
            raise EventUnexpectedStatus

        cache_key = str(event_id)
        cached = _seats_cache.get(cache_key)
        if cached is not None:
            return cached

        data = await self.client.get_seats(str(event_id))
        seats = data.get("seats", [])
        _seats_cache.set(cache_key, seats)
        return seats