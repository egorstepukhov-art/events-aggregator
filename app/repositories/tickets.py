from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Ticket


class TicketRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_ticket_id(self, ticket_id: UUID) -> Ticket | None:
        result = await self.session.execute(select(Ticket).where(Ticket.ticket_id == ticket_id))
        return result.scalar_one_or_none()

    async def create(
        self,
        *,
        ticket_id: UUID,
        event_id: UUID,
        first_name: str,
        last_name: str,
        email: str,
        seat: str,
    ) -> Ticket:
        ticket = Ticket(
            ticket_id=ticket_id,
            event_id=event_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            seat=seat,
        )
        self.session.add(ticket)
        await self.session.flush()
        return ticket

    async def delete(self, ticket: Ticket) -> None:
        await self.session.delete(ticket)
