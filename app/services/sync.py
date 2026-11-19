from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.events_provider import EventsProviderClient
from app.clients.paginator import EventsPaginator
from app.models import Event, Place, SyncMeta


class SyncService:
    def __init__(self, session: AsyncSession, client: EventsProviderClient | None = None):
        self.session = session
        self.client = client or EventsProviderClient()

    async def get_last_changed_at(self) -> str:
        """Возвращает дату для инкрементальной синхронизации."""
        result = await self.session.execute(select(SyncMeta).limit(1))
        meta = result.scalar_one_or_none()

        if meta and meta.last_changed_at:
            return meta.last_changed_at.date().isoformat()
        return "2000-01-01"

    async def update_sync_meta(self, last_changed_at: datetime | None, status: str, message: str = ""):
        result = await self.session.execute(select(SyncMeta).limit(1))
        meta = result.scalar_one_or_none()

        if not meta:
            meta = SyncMeta()
            self.session.add(meta)

        meta.last_sync_time = datetime.now(timezone.utc)
        meta.last_changed_at = last_changed_at
        meta.sync_status = status
        meta.message = message
        await self.session.commit()

    async def sync_events(self) -> dict:
        """Основной метод синхронизации."""
        try:
            changed_at = await self.get_last_changed_at()
            max_changed_at = None
            total_events = 0

            paginator = EventsPaginator(self.client, changed_at=changed_at)

            async for page in paginator:
                for event_data in page:
                    await self._upsert_event(event_data)
                    total_events += 1

                    event_changed = event_data.get("changed_at")
                    if event_changed:
                        dt = datetime.fromisoformat(event_changed)
                        if max_changed_at is None or dt > max_changed_at:
                            max_changed_at = dt

                await self.session.commit()

            await self.update_sync_meta(max_changed_at, "success", f"Synced {total_events} events")
            return {"status": "success", "synced": total_events}

        except Exception as e:
            await self.session.rollback()
            await self.update_sync_meta(None, "error", str(e))
            raise

    async def _upsert_event(self, data: dict):
        """Добавляет или обновляет событие и площадку."""
        place_data = data["place"]

        # Place
        place = await self.session.get(Place, place_data["id"])
        if not place:
            place = Place(id=place_data["id"])
            self.session.add(place)

        place.name = place_data["name"]
        place.city = place_data["city"]
        place.address = place_data["address"]
        place.seats_pattern = place_data["seats_pattern"]
        place.created_at = datetime.fromisoformat(place_data["created_at"])
        place.changed_at = datetime.fromisoformat(place_data["changed_at"])

        # Event
        event = await self.session.get(Event, data["id"])
        if not event:
            event = Event(id=data["id"])
            self.session.add(event)

        event.name = data["name"]
        event.place_id = place_data["id"]
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