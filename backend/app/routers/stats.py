from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import OccupancyStats
from app.schemas import StatsResponse

router = APIRouter(prefix="/api", tags=["stats"])


@router.get("/stats", response_model=StatsResponse)
async def get_stats(db: AsyncSession = Depends(get_db)):
    """Return the current occupancy statistics."""
    result = await db.execute(select(OccupancyStats).where(OccupancyStats.id == 1))
    stats = result.scalar_one_or_none()
    if stats is None:
        return StatsResponse(people_inside=0, entries_today=0, exits_today=0)
    return StatsResponse(
        people_inside=stats.people_inside,
        entries_today=stats.entries_today,
        exits_today=stats.exits_today,
    )
