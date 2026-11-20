from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.events_provider import EventsProviderClient
from app.clients.paginator import EventsPaginator
from app.enums import SyncStatus
from app.repositories.events import EventRepository, SyncMetaRepository


class SyncService:
    def __init__(self, session: AsyncSession, client: EventsProviderClient | None = None):
        self.session = session
        self.client = client or EventsProviderClient()
        self.events = EventRepository(session)
        self.meta = SyncMetaRepository(session)

    async def get_last_changed_at(self) -> str:
        meta = await self.meta.get()
        if meta and meta.last_changed_at:
            return meta.last_changed_at.date().isoformat()
        return "2000-01-01"

    async def sync_events(self) -> dict:
        try:
            changed_at = await self.get_last_changed_at()
            max_changed_at: datetime | None = None
            total_events = 0

            paginator = EventsPaginator(self.client, changed_at=changed_at)

            async for page in paginator:
                for event_data in page:
                    await self.events.upsert_place(event_data["place"])
                    await self.events.upsert_event(event_data)
                    total_events += 1

                    event_changed = event_data.get("changed_at")
                    if event_changed:
                        dt = datetime.fromisoformat(event_changed)
                        if max_changed_at is None or dt > max_changed_at:
                            max_changed_at = dt

                await self.session.commit()

            await self.meta.update(
                last_changed_at=max_changed_at,
                status=SyncStatus.SUCCESS,
                message=f"Synced {total_events} events",
            )
            await self.session.commit()
            return {"status": "success", "synced": total_events}

        except Exception as e:
            await self.session.rollback()
            await self.meta.update(
                last_changed_at=None,
                status=SyncStatus.ERROR,
                message=str(e),
            )
            await self.session.commit()
            raise