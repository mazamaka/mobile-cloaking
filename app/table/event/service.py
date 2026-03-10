"""Event processing service."""

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.table.app.model import App
from app.table.client.model import Client
from app.table.event.model import Event
from app.table.event.schemas import EventRequest
from app.utils.logger import logger


class EventService:
    """Handle /client/event requests: validate and persist analytics events."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_client(self, internal_id: str) -> Client | None:
        """Find client by internal_id."""
        stmt = select(Client).where(Client.internal_id == internal_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_app(self, bundle_id: str) -> App | None:
        """Find app by bundle_id."""
        stmt = select(App).where(App.bundle_id == bundle_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def process_event(self, data: EventRequest) -> bool:
        """Process event request and persist to database.

        Returns:
            True if event was saved, False if client or app not found.
        """
        client = await self.get_client(data.ids.internal_id)
        if not client:
            logger.warning(f"Event from unknown client: {data.ids.internal_id}")
            return False

        app = await self.get_app(data.app.bundle_id)
        if not app:
            logger.warning(f"Event for unknown app: {data.app.bundle_id}")
            return False

        event_ts = datetime.fromtimestamp(data.event.ts, tz=UTC)

        event = Event(
            client_id=client.id,
            app_id=app.id,
            name=data.event.name,
            event_ts=event_ts,
            props=data.event.props,
            app_version=data.app.version,
        )
        self.session.add(event)
        await self.session.flush()

        logger.info(
            f"Event saved: {data.event.name} from client={data.ids.internal_id}"
        )
        return True
