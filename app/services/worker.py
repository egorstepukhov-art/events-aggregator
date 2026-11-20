import asyncio
import logging
from datetime import UTC, datetime

from app.config import get_settings
from app.database import async_session
from app.services.sync import SyncService

logger = logging.getLogger(__name__)

_sync_lock = asyncio.Lock()


async def run_sync_once() -> None:
    async with _sync_lock:
        async with async_session() as session:
            service = SyncService(session)
            try:
                result = await service.sync_events()
                logger.info("Periodic sync done: %s", result)
            except Exception:
                logger.exception("Periodic sync failed")


async def periodic_sync_loop() -> None:
    settings = get_settings()
    interval = settings.sync_interval_hours * 3600

    await asyncio.sleep(5)

    while True:
        started = datetime.now(UTC)
        logger.info("Starting periodic sync at %s", started.isoformat())
        await run_sync_once()
        logger.info("Periodic sync finished, sleeping %s seconds", interval)
        await asyncio.sleep(interval)
