from datetime import datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Event, Place


class EventRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, event_id: UUID) -> Event | None:
        result = await self.session.execute(
            select(Event).options(selectinload(Event.place)).where(Event.id == event_id)
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        *,
        date_from: str | None,
        page: int,
        page_size: int,
    ) -> tuple[list[Event], int]:
        base = select(Event)
        if date_from:
            dt = datetime.strptime(date_from, "%Y-%m-%d")
            base = base.where(Event.event_time >= dt)

        count_query = select(func.count()).select_from(base.subquery())
        total = (await self.session.execute(count_query)).scalar() or 0

        query = (
            base.options(selectinload(Event.place))
            .order_by(Event.event_time.asc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all()), total

    async def upsert_place(self, data: dict) -> None:
        place = await self.session.get(Place, data["id"])
        if not place:
            place = Place(id=data["id"])
            self.session.add(place)

        place.name = data["name"]
        place.city = data["city"]
        place.address = data["address"]
        place.seats_pattern = data["seats_pattern"]
        place.created_at = datetime.fromisoformat(data["created_at"])
        place.changed_at = datetime.fromisoformat(data["changed_at"])

    async def upsert_event(self, data: dict) -> None:
        event = await self.session.get(Event, data["id"])
        if not event:
            event = Event(id=data["id"])
            self.session.add(event)

        event.name = data["name"]
        event.place_id = data["place"]["id"]
        event.event_time = datetime.fromisoformat(data["event_time"])
        event.registration_deadline = datetime.fromisoformat(data["registration_deadline"])
        event.status = data["status"]
        event.number_of_visitors = data.get("number_of_visitors", 0)
        event.created_at = datetime.fromisoformat(data["created_at"])
        event.changed_at = datetime.fromisoformat(data["changed_at"])
        event.status_changed_at = (
            datetime.fromisoformat(data["status_changed_at"])
            if data.get("status_changed_at")
            else None
        )


class SyncMetaRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self):
        from app.models import SyncMeta

        result = await self.session.execute(select(SyncMeta).limit(1))
        return result.scalar_one_or_none()

    async def update(
        self,
        *,
        last_changed_at: datetime | None,
        status: str,
        message: str = "",
    ) -> None:
        from app.models import SyncMeta

        meta = await self.get()
        if not meta:
            meta = SyncMeta()
            self.session.add(meta)

        if last_changed_at is not None:
            meta.last_changed_at = last_changed_at

        meta.last_sync_time = datetime.now(tz=None)
        meta.sync_status = status
        meta.message = message