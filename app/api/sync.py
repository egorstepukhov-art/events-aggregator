from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.sync import SyncService
from app.services.worker import _sync_lock

router = APIRouter(prefix="/api/sync", tags=["Sync"])


@router.post("/trigger")
async def trigger_sync(db: AsyncSession = Depends(get_db)):
    async with _sync_lock:
        service = SyncService(db)
        result = await service.sync_events()
        return result
