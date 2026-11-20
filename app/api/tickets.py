from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.events_provider import EventsProviderClient
from app.database import get_db
from app.repositories.events import EventRepository
from app.repositories.tickets import TicketRepository
from app.services.events import EventNotFound, EventUnexpectedStatus
from app.services.tickets import (
    CancelTicketUsecase,
    CreateTicketUsecase,
    TicketNotFound,
)

router = APIRouter(prefix="/api/tickets", tags=["Tickets"])


class RegisterRequest(BaseModel):
    event_id: UUID
    first_name: str
    last_name: str
    email: str
    seat: str


def get_event_repo(db: AsyncSession = Depends(get_db)) -> EventRepository:
    return EventRepository(db)


def get_ticket_repo(db: AsyncSession = Depends(get_db)) -> TicketRepository:
    return TicketRepository(db)


def get_client() -> EventsProviderClient:
    return EventsProviderClient()


@router.post("", status_code=201)
async def register_ticket(
    data: RegisterRequest,
    events: EventRepository = Depends(get_event_repo),
    tickets: TicketRepository = Depends(get_ticket_repo),
    client: EventsProviderClient = Depends(get_client),
):
    usecase = CreateTicketUsecase(client, events, tickets)
    try:
        ticket_id = await usecase.do(
            event_id=data.event_id,
            first_name=data.first_name,
            last_name=data.last_name,
            email=data.email,
            seat=data.seat,
        )
    except EventNotFound:
        raise HTTPException(status_code=404, detail="Event not found") from None
    except EventUnexpectedStatus:
        raise HTTPException(status_code=400, detail="Event is not published") from None

    return {"ticket_id": str(ticket_id)}


@router.delete("/{ticket_id}")
async def cancel_ticket(
    ticket_id: UUID,
    tickets: TicketRepository = Depends(get_ticket_repo),
    client: EventsProviderClient = Depends(get_client),
):
    usecase = CancelTicketUsecase(client, tickets)
    try:
        await usecase.do(ticket_id)
    except TicketNotFound:
        raise HTTPException(status_code=404, detail="Ticket not found") from None

    return {"success": True}