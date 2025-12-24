from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.table.app.enums import AppMode
from app.table.app.model import App
from app.table.client.model import Client
from app.table.client.schemas import (
    InitRequest,
    InitResponseCasino,
    InitResponseNative,
    PromptsConfig,
    UpdateConfig,
)
from app.utils.logger import logger
from config import SETTINGS


class InitService:
    """Service for handling /client/init requests."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_or_create_app(self, bundle_id: str) -> App:
        """Get existing app or create a new one."""
        stmt = select(App).where(App.bundle_id == bundle_id)
        result = await self.session.execute(stmt)
        app = result.scalar_one_or_none()

        if not app:
            app = App(
                bundle_id=bundle_id,
                rate_delay_sec=SETTINGS.default_rate_delay_sec,
                push_delay_sec=SETTINGS.default_push_delay_sec,
            )
            self.session.add(app)
            await self.session.flush()
            logger.info(f"Created new app: {bundle_id}")

        return app

    async def get_or_create_client(
        self, app: App, data: InitRequest
    ) -> tuple[Client, bool]:
        """Get existing client or create a new one. Returns (client, is_new)."""
        stmt = select(Client).where(Client.internal_id == data.ids.internal_id)
        result = await self.session.execute(stmt)
        client = result.scalar_one_or_none()

        is_new = client is None

        if is_new:
            client = Client(
                internal_id=data.ids.internal_id,
                app_id=app.id,
                app_version=data.app.version,
                language=data.device.language,
                timezone=data.device.timezone,
                region=data.device.region,
                att_status=data.privacy.att,
                idfa=data.ids.idfa,
                appsflyer_id=data.attribution.appsflyer_id if data.attribution else None,
                push_token=data.push.token if data.push else None,
            )
            self.session.add(client)
            logger.info(f"Created new client: {data.ids.internal_id}")
        else:
            # Update existing client
            client.app_version = data.app.version
            client.language = data.device.language
            client.timezone = data.device.timezone
            client.region = data.device.region
            client.att_status = data.privacy.att
            client.idfa = data.ids.idfa
            if data.attribution:
                client.appsflyer_id = data.attribution.appsflyer_id
            if data.push:
                client.push_token = data.push.token
            client.last_seen_at = datetime.utcnow()
            client.sessions_count += 1

        await self.session.flush()
        return client, is_new

    async def process_init(
        self, data: InitRequest
    ) -> tuple[int, InitResponseNative | InitResponseCasino]:
        """Process init request and return (status_code, response)."""
        app = await self.get_or_create_app(data.app.bundle_id)
        client, is_new = await self.get_or_create_client(app, data)

        # Build response
        status_code, response = DecisionEngine.decide(app)

        logger.info(
            f"Init: app={app.bundle_id}, client={client.internal_id}, "
            f"mode={app.mode}, status={status_code}, new={is_new}"
        )

        return status_code, response


class DecisionEngine:
    """Decides response based on app mode."""

    @staticmethod
    def decide(app: App) -> tuple[int, InitResponseNative | InitResponseCasino]:
        """Return (status_code, response_body)."""
        prompts = PromptsConfig(
            rate_delay_sec=app.rate_delay_sec,
            push_delay_sec=app.push_delay_sec,
        )

        update = None
        if app.min_version or app.latest_version:
            update = UpdateConfig(
                min_version=app.min_version,
                latest_version=app.latest_version,
                mode=app.update_mode,
                appstore_url=app.appstore_url,
            )

        if app.mode == AppMode.CASINO and app.casino_url:
            return 400, InitResponseCasino(
                result=app.casino_url,
                prompts=prompts,
                update=update,
            )

        return 200, InitResponseNative(
            prompts=prompts,
            update=update,
        )
