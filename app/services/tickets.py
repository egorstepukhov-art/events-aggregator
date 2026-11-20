from uuid import UUID

from app.enums import EventStatus
from app.repositories.events import EventRepository
from app.repositories.tickets import TicketRepository
from app.services.events import EventNotFound, EventUnexpectedStatus, _seats_cache


class TicketNotFound(Exception):
    pass


class CreateTicketUsecase:
    def __init__(self, client, events: EventRepository, tickets: TicketRepository):
        self.client = client
        self.events = events
        self.tickets = tickets

    async def do(
        self,
        *,
        event_id: UUID,
        first_name: str,
        last_name: str,
        email: str,
        seat: str,
    ) -> UUID:
        event = await self.events.get(event_id)
        if not event:
            raise EventNotFound
        if event.status != EventStatus.PUBLISHED:
            raise EventUnexpectedStatus

        response = await self.client.register(
            event_id=str(event_id),
            first_name=first_name,
            last_name=last_name,
            email=email,
            seat=seat,
        )
        ticket_id = UUID(response["ticket_id"])

        await self.tickets.create(
            ticket_id=ticket_id,
            event_id=event_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            seat=seat,
        )
        _seats_cache.invalidate(str(event_id))
        return ticket_id


class CancelTicketUsecase:
    def __init__(self, client, tickets: TicketRepository):
        self.client = client
        self.tickets = tickets

    async def do(self, ticket_id: UUID) -> None:
        ticket = await self.tickets.get_by_ticket_id(ticket_id)
        if not ticket:
            raise TicketNotFound

        await self.client.unregister(
            event_id=str(ticket.event_id),
            ticket_id=str(ticket.ticket_id),
        )
        await self.tickets.delete(ticket)
        _seats_cache.invalidate(str(ticket.event_id))