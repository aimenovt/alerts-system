from datetime import datetime
from typing import Any, TYPE_CHECKING

from pydantic import BaseModel, ConfigDict

if TYPE_CHECKING:
    from app.models.event import Event


class EventMessage(BaseModel):
    """Broker payload for async event processing."""

    model_config = ConfigDict(from_attributes=True)

    event_id: str
    event_type: str
    payload: dict[str, Any]
    owner_id: str
    created_at: datetime

    @classmethod
    def from_event(cls, event: "Event") -> "EventMessage":
        return cls(
            event_id=event.id,
            event_type=event.event_type,
            payload=event.payload,
            owner_id=event.owner_id,
            created_at=event.created_at,
        )
