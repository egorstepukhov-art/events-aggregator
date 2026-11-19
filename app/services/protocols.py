from typing import Any, Protocol
from uuid import UUID

from app.models import Event, Ticket


class EventsProviderClientProtocol(Protocol):
    async def get_events(self, changed_at: str = "2000-01-01", cursor: str | None = None) -> dict[str, Any]: ...
    async def get_seats(self, event_id: str) -> dict[str, Any]: ...
    async def register(
        self, event_id: str, first_name: str, last_name: str, email: str, seat: str
    ) -> dict[str, Any]: ...
    async def unregister(self, event_id: str, ticket_id: str) -> dict[str, Any]: ...


class EventRepositoryProtocol(Protocol):
    async def get(self, event_id: UUID) -> Event | None: ...
    async def list(
        self,
        *,
        date_from: str | None,
        page: int,
        page_size: int,
    ) -> tuple[list[Event], int]: ...


class TicketRepositoryProtocol(Protocol):
    async def get_by_ticket_id(self, ticket_id: UUID) -> Ticket | None: ...
    async def create(
        self,
        *,
        ticket_id: UUID,
        event_id: UUID,
        first_name: str,
        last_name: str,
        email: str,
        seat: str,
    ) -> Ticket: ...
    async def delete(self, ticket: Ticket) -> None: ...