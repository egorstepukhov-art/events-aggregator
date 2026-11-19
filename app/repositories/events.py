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


class PlaceRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, place_id: UUID) -> Place | None:
        return await self.session.get(Place, place_id)