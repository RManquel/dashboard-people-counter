import asyncio
import logging

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import init_db
from app.routers import ws, health, alert, stats, history

logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up — initializing database…")
    await init_db()

    # Start optional MQTT listener as background task
    from app.mqtt import start_mqtt_listener
    from app.routers.alert import process_alert

    mqtt_task = asyncio.create_task(start_mqtt_listener(process_alert))

    yield

    # Shutdown
    mqtt_task.cancel()
    try:
        await mqtt_task
    except asyncio.CancelledError:
        pass
    logger.info("Shutdown complete.")


def create_app() -> FastAPI:
    app = FastAPI(
        title="Stadium People Counter API",
        description="Real-time stadium occupancy tracking API",
        version="1.0.0",
        lifespan=lifespan,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routers
    app.include_router(health.router)
    app.include_router(alert.router)
    app.include_router(stats.router)
    app.include_router(history.router)
    app.include_router(ws.router)

    return app


app = create_app()
