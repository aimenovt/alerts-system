from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.event import Event, EventStatus


class EventRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, *, event_type: str, payload: dict, owner_id: str) -> Event:
        event = Event(event_type=event_type, payload=payload, owner_id=owner_id)
        self.session.add(event)
        await self.session.commit()
        await self.session.refresh(event)
        return event

    async def get_by_id(self, event_id: str) -> Event | None:
        return await self.session.get(Event, event_id)

    async def update_status(self, event_id: str, status: EventStatus) -> Event | None:
        event = await self.get_by_id(event_id)
        if event is None:
            return None
        event.status = status
        await self.session.commit()
        await self.session.refresh(event)
        return event

    async def list_by_owner(self, owner_id: str) -> list[Event]:
        statement = select(Event).where(Event.owner_id == owner_id).order_by(Event.created_at.desc())
        result = await self.session.execute(statement)
        return list(result.scalars().all())
