from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.event import EventStatus


class EventCreate(BaseModel):
    event_type: str = Field(min_length=2, max_length=120)
    payload: dict[str, Any]


class EventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    event_type: str
    payload: dict[str, Any]
    status: EventStatus
    owner_id: str
    created_at: datetime
