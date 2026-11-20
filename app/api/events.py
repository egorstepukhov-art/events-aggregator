from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.events_provider import EventsProviderClient
from app.database import get_db
from app.repositories.events import EventRepository
from app.services.events import (
    EventNotFound,
    EventUnexpectedStatus,
    GetEventsUsecase,
    GetEventUsecase,
    GetSeatsUsecase,
)

router = APIRouter(prefix="/api/events", tags=["Events"])


def get_event_repo(db: AsyncSession = Depends(get_db)) -> EventRepository:
    return EventRepository(db)


def get_client() -> EventsProviderClient:
    return EventsProviderClient()


@router.get("")
async def get_events(
    request: Request,
    date_from: str | None = Query(None, description="YYYY-MM-DD"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    repo: EventRepository = Depends(get_event_repo),
):
    if date_from:
        try:
            datetime.strptime(date_from, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid date_from format. Use YYYY-MM-DD",
            ) from None

    usecase = GetEventsUsecase(repo)
    events, total = await usecase.do(date_from=date_from, page=page, page_size=page_size)

    next_url = None
    prev_url = None
    if page * page_size < total:
        next_url = str(request.url.include_query_params(page=page + 1, page_size=page_size))
    if page > 1:
        prev_url = str(request.url.include_query_params(page=page - 1, page_size=page_size))

    return {
        "count": total,
        "next": next_url,
        "previous": prev_url,
        "results": [
            {
                "id": str(e.id),
                "name": e.name,
                "place": {
                    "id": str(e.place.id),
                    "name": e.place.name,
                    "city": e.place.city,
                    "address": e.place.address,
                },
                "event_time": e.event_time.isoformat(),
                "registration_deadline": e.registration_deadline.isoformat(),
                "status": e.status,
                "number_of_visitors": e.number_of_visitors,
            }
            for e in events
        ],
    }


@router.get("/{event_id}")
async def get_event(
    event_id: UUID,
    repo: EventRepository = Depends(get_event_repo),
):
    usecase = GetEventUsecase(repo)
    try:
        event = await usecase.do(event_id)
    except EventNotFound:
        raise HTTPException(status_code=404, detail="Event not found") from None

    return {
        "id": str(event.id),
        "name": event.name,
        "place": {
            "id": str(event.place.id),
            "name": event.place.name,
            "city": event.place.city,
            "address": event.place.address,
            "seats_pattern": event.place.seats_pattern,
        },
        "event_time": event.event_time.isoformat(),
        "registration_deadline": event.registration_deadline.isoformat(),
        "status": event.status,
        "number_of_visitors": event.number_of_visitors,
    }


@router.get("/{event_id}/seats")
async def get_seats(
    event_id: UUID,
    repo: EventRepository = Depends(get_event_repo),
    client: EventsProviderClient = Depends(get_client),
):
    usecase = GetSeatsUsecase(repo, client)
    try:
        seats = await usecase.do(event_id)
    except EventNotFound:
        raise HTTPException(status_code=404, detail="Event not found") from None
    except EventUnexpectedStatus:
        raise HTTPException(status_code=400, detail="Event is not published") from None

    return {"event_id": str(event_id), "available_seats": seats}