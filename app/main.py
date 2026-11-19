import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import events, sync, tickets
from app.config import get_settings
from app.services.worker import periodic_sync_loop

logging.basicConfig(level=logging.INFO)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(periodic_sync_loop())
    try:
        yield
    finally:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass


app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    lifespan=lifespan,
)

app.include_router(sync.router)
app.include_router(events.router)
app.include_router(tickets.router)


@app.get("/api/health")
async def health_check():
    return {"status": "ok"}