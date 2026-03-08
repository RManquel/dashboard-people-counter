import datetime
from sqlalchemy import Integer, String, BigInteger, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    device_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    direction: Mapped[str] = mapped_column(String(8), nullable=False)  # "in" | "out"
    # Unix timestamp provided by the device (external clock)
    timestamp: Mapped[int] = mapped_column(BigInteger, nullable=False)
    # Server-side insertion time
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class OccupancyStats(Base):
    """Single-row table that always holds the current aggregate stats."""

    __tablename__ = "occupancy_stats"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    people_inside: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    entries_today: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    exits_today: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
