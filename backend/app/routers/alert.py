import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import Event, OccupancyStats
from app.schemas import AlertPayload, StatsResponse
from app.websocket import manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["alert"])


async def _get_or_create_stats(db: AsyncSession) -> OccupancyStats:
    result = await db.execute(select(OccupancyStats).where(OccupancyStats.id == 1))
    stats = result.scalar_one_or_none()
    if stats is None:
        stats = OccupancyStats(id=1, people_inside=0, entries_today=0, exits_today=0)
        db.add(stats)
        await db.flush()
    return stats


async def process_alert(payload: AlertPayload, db: AsyncSession) -> StatsResponse:
    """Core business logic shared by REST and MQTT handlers."""
    # Persist event
    event = Event(
        device_id=payload.device_id,
        direction=payload.direction,
        timestamp=payload.timestamp,
    )
    db.add(event)

    # Update stats
    stats = await _get_or_create_stats(db)
    if payload.direction == "in":
        stats.people_inside += 1
        stats.entries_today += 1
    else:
        stats.people_inside = max(0, stats.people_inside - 1)
        stats.exits_today += 1

    await db.commit()
    await db.refresh(stats)

    response = StatsResponse(
        people_inside=stats.people_inside,
        entries_today=stats.entries_today,
        exits_today=stats.exits_today,
    )

    # Broadcast to all WebSocket clients
    await manager.broadcast({
        "event": "stats_update",
        "data": response.model_dump(),
    })

    return response


@router.post("/alert", response_model=StatsResponse, status_code=200)
async def receive_alert(payload: AlertPayload, db: AsyncSession = Depends(get_db)):
    """Receive a people counter event and update occupancy."""
    try:
        return await process_alert(payload, db)
    except Exception as exc:
        logger.error("Error processing alert: %s", exc)
        raise HTTPException(status_code=500, detail="Internal server error")
