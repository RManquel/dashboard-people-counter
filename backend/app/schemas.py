from typing import Literal
from pydantic import BaseModel, field_validator


class AlertPayload(BaseModel):
    device_id: str
    direction: Literal["in", "out"]
    timestamp: int

    @field_validator("device_id")
    @classmethod
    def device_id_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("device_id must not be empty")
        return v.strip()


class StatsResponse(BaseModel):
    people_inside: int
    entries_today: int
    exits_today: int


class HealthResponse(BaseModel):
    status: str


class ChartDataPoint(BaseModel):
    minute: str          # ISO 8601 truncated to minute, e.g. "2024-03-10T14:35"
    entries: int
    exits: int


class WebSocketMessage(BaseModel):
    event: str           # e.g. "stats_update"
    data: StatsResponse
