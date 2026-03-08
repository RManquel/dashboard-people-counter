from datetime import datetime, timezone, timedelta
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case

from app.database import get_db
from app.models import Event
from app.schemas import ChartDataPoint

router = APIRouter(prefix="/api", tags=["history"])


@router.get("/history", response_model=List[ChartDataPoint])
async def get_history(db: AsyncSession = Depends(get_db)):
    """
    Return per-minute aggregated entries and exits for the last 60 minutes.
    Uses the server-side `created_at` column for time bucketing.
    """
    now = datetime.now(timezone.utc)
    since = now - timedelta(hours=1)
    since_ts = int(since.timestamp())

    # Aggregate using created_at truncated to minute
    result = await db.execute(
        select(
            func.date_trunc("minute", Event.created_at).label("minute"),
            func.sum(case((Event.direction == "in", 1), else_=0)).label("entries"),
            func.sum(case((Event.direction == "out", 1), else_=0)).label("exits"),
        )
        .where(Event.created_at >= since)
        .group_by(func.date_trunc("minute", Event.created_at))
        .order_by(func.date_trunc("minute", Event.created_at))
    )

    rows = result.all()
    return [
        ChartDataPoint(
            minute=row.minute.strftime("%Y-%m-%dT%H:%M"),
            entries=int(row.entries or 0),
            exits=int(row.exits or 0),
        )
        for row in rows
    ]
