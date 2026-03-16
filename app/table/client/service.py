"""Core business logic: client initialization and mode decision."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from app.utils.helpers import utc_now

if TYPE_CHECKING:
    from starlette.requests import Request
from app.table.app.enums import AppMode
from app.table.app.model import App
from app.table.client.model import Client
from app.table.client.schemas import (
    InitRequest,
    InitResponse,
    PromptsConfig,
    UpdateConfig,
)
from app.table.geo.model import Geo
from app.table.link.model import Link
from app.table.offer.model import Offer
from app.utils.logger import logger
from app.utils.version import check_update


class InitService:
    """Handle /client/init requests: find app/client, resolve offer."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_app(self, bundle_id: str) -> App | None:
        """Get app by bundle_id with Redis cache. Returns None if not found."""
        from app.cache.redis import cache

        # Try cache first
        if cache.available:
            cached = await cache.get_app_dict(bundle_id)
            if cached:
                stmt = select(App).where(App.id == cached["id"])
                result = await self.session.execute(stmt)
                return result.scalar_one_or_none()

        # DB lookup
        stmt = select(App).where(App.bundle_id == bundle_id)
        result = await self.session.execute(stmt)
        app = result.scalar_one_or_none()

        # Cache for next time
        if app and cache.available:
            await cache.set_app_dict(
                bundle_id, {"id": app.id, "bundle_id": app.bundle_id}
            )

        return app

    async def get_or_create_geo(self, code: str) -> Geo:
        """Get existing Geo by code or auto-create a new one."""
        code_upper = code.upper()
        stmt = select(Geo).where(Geo.code == code_upper)
        result = await self.session.execute(stmt)
        geo = result.scalar_one_or_none()
        if geo:
            return geo

        geo = Geo(
            code=code_upper,
            name=get_country_name(code_upper),
            is_active=True,
            is_default=False,
        )
        self.session.add(geo)
        await self.session.flush()
        logger.info(f"Auto-created Geo: {code_upper} ({geo.name})")
        return geo

    async def get_or_create_client(
        self,
        app: App,
        data: InitRequest,
        *,
        cf_country: str | None = None,
        geo_id: int | None = None,
    ) -> tuple[Client, bool]:
        """Get existing client or create a new one.

        Returns:
            Tuple of (client, is_new) where is_new indicates first-time client.
        """
        stmt = select(Client).where(Client.internal_id == data.ids.internal_id)
        result = await self.session.execute(stmt)
        client = result.scalar_one_or_none()

        is_new = client is None

        if is_new:
            client = Client(
                internal_id=data.ids.internal_id,
                app_id=app.id,
                geo_id=geo_id,
                app_version=data.app.version,
                language=data.device.language,
                timezone=data.device.timezone,
                region=data.device.region,
                cf_country=cf_country,
                att_status=data.privacy.att,
                idfa=data.ids.idfa,
                appsflyer_id=data.attribution.appsflyer_id
                if data.attribution
                else None,
                push_token=data.push.token if data.push else None,
            )
            self.session.add(client)
        else:
            client.geo_id = geo_id
            client.app_version = data.app.version
            client.language = data.device.language
            client.timezone = data.device.timezone
            client.region = data.device.region
            client.cf_country = cf_country
            client.att_status = data.privacy.att
            client.idfa = data.ids.idfa
            if data.attribution:
                client.appsflyer_id = data.attribution.appsflyer_id
            if data.push and data.push.token is not None:
                client.push_token = data.push.token
            client.last_seen_at = utc_now()
            client.sessions_count += 1

        await self.session.flush()
        return client, is_new

    @staticmethod
    def _apply_link_filters(
        stmt: Select,  # type: ignore[type-arg]
        *,
        language: str | None = None,
        app_version: str | None = None,
        att_status: str | None = None,
    ) -> Select:  # type: ignore[type-arg]
        """Apply nullable link filters: NULL in DB = matches any value."""
        if language:
            base_lang = language.split("-")[0] if "-" in language else language
            stmt = stmt.where(or_(Link.language.is_(None), Link.language == base_lang))
        else:
            stmt = stmt.where(Link.language.is_(None))

        if att_status:
            stmt = stmt.where(
                or_(Link.att_status.is_(None), Link.att_status == att_status)
            )
        else:
            stmt = stmt.where(Link.att_status.is_(None))

        if app_version:
            stmt = stmt.where(
                or_(Link.min_version.is_(None), Link.min_version <= app_version)
            )
            stmt = stmt.where(
                or_(Link.max_version.is_(None), Link.max_version >= app_version)
            )

        return stmt

    async def get_offer_for_geo(
        self,
        app_id: int,
        region: str,
        *,
        language: str | None = None,
        app_version: str | None = None,
        att_status: str | None = None,
    ) -> tuple[Offer, Link] | None:
        """Find best offer+link for app, geo, and device filters.

        Filters on Link (NULL = matches any):
        - language: base language code (en, ru)
        - app_version: must be between min_version..max_version
        - att_status: ATT status string

        Priority order:
        1. Exact geo match with matching filters
        2. Default geo with matching filters
        3. None if no offers found
        """
        effective_priority = func.coalesce(Link.priority, Offer.priority)
        filter_kwargs = dict(
            language=language, app_version=app_version, att_status=att_status
        )

        # Try exact geo match
        stmt = (
            select(Offer, Link)
            .join(Link, Offer.id == Link.offer_id)
            .join(Geo, Link.geo_id == Geo.id)
            .where(
                Link.app_id == app_id,
                Link.is_active == True,  # noqa: E712
                Offer.is_active == True,  # noqa: E712
                Geo.is_active == True,  # noqa: E712
                Geo.code == region,
            )
            .order_by(effective_priority.desc())
            .limit(1)
        )
        stmt = self._apply_link_filters(stmt, **filter_kwargs)
        result = await self.session.execute(stmt)
        row = result.first()

        if row:
            return row[0], row[1]

        # Fallback to default geo
        stmt = (
            select(Offer, Link)
            .join(Link, Offer.id == Link.offer_id)
            .join(Geo, Link.geo_id == Geo.id)
            .where(
                Link.app_id == app_id,
                Link.is_active == True,  # noqa: E712
                Offer.is_active == True,  # noqa: E712
                Geo.is_active == True,  # noqa: E712
                Geo.is_default == True,  # noqa: E712
            )
            .order_by(effective_priority.desc())
            .limit(1)
        )
        stmt = self._apply_link_filters(stmt, **filter_kwargs)
        result = await self.session.execute(stmt)
        row = result.first()

        if row:
            return row[0], row[1]

        return None

    async def process_init(
        self,
        data: InitRequest,
        request: "Request | None" = None,
        api_key: str | None = None,
    ) -> InitResponse:
        """Process init request: resolve app, client, offer, and build response."""
        from app.table.init_log.model import InitLog

        # Extract CF headers
        cf_country: str | None = None
        client_ip: str | None = None
        headers_dict: dict[str, str] = {}
        if request:
            cf_country = request.headers.get("cf-ipcountry")
            client_ip = request.headers.get("cf-connecting-ip")
            if not client_ip and request.client:
                client_ip = request.client.host
            headers_dict = dict(request.headers)

        app = await self.get_app(data.app.bundle_id)

        if not app:
            from fastapi import HTTPException

            raise HTTPException(status_code=404, detail="App not found")

        if app.api_key and app.api_key != api_key:
            from fastapi import HTTPException

            raise HTTPException(status_code=401, detail="Invalid API key")

        # Choose geo source based on app setting
        from app.table.app.enums import GeoSource

        if app.geo_source == GeoSource.DEVICE:
            geo_region = data.device.region
        else:
            geo_region = cf_country or data.device.region

        # Resolve Geo (auto-create if not in DB)
        geo = await self.get_or_create_geo(geo_region)

        client, is_new = await self.get_or_create_client(
            app, data, cf_country=cf_country, geo_id=geo.id
        )

        offer_link = None
        if app.mode == AppMode.CASINO:
            offer_link = await self.get_offer_for_geo(
                app.id,
                geo_region,
                language=data.device.language,
                app_version=data.app.version,
                att_status=data.privacy.att.value,
            )

        offer = offer_link[0] if offer_link else None
        link = offer_link[1] if offer_link else None

        response = DecisionEngine.decide(
            app=app,
            offer=offer,
            link=link,
            app_version=data.app.version,
        )

        result_mode = "casino" if response.result else "native"

        logger.info(
            f"Init: app={app.bundle_id}, client={client.internal_id}, "
            f"mode={app.mode}, geo={geo_region} (device={data.device.region}), "
            f"offer={offer.name if offer else None}, "
            f"{result_mode}, new={is_new}, ip={client_ip}"
        )

        # Save init log
        init_log = InitLog(
            client_id=client.id,
            ip=client_ip,
            cf_country=cf_country,
            bundle_id=data.app.bundle_id,
            result_mode=result_mode,
            request_headers=headers_dict,
            request_body=data.model_dump(mode="json"),
            response_code=200,
            response_body=response.model_dump(mode="json"),
        )
        self.session.add(init_log)

        return response


class DecisionEngine:
    """Build client response based on app mode and resolved offer."""

    @staticmethod
    def decide(
        app: App,
        offer: Offer | None = None,
        link: Link | None = None,
        app_version: str | None = None,
    ) -> InitResponse:
        """Build InitResponse with per-link overrides and server-side version check."""
        # Per-link overrides or app defaults
        rate_delay = (
            link.rate_delay_sec
            if link and link.rate_delay_sec is not None
            else app.rate_delay_sec
        )
        push_delay = (
            link.push_delay_sec
            if link and link.push_delay_sec is not None
            else app.push_delay_sec
        )
        icon_name = (
            link.icon_name if link and link.icon_name is not None else app.icon_name
        )

        prompts = PromptsConfig(
            rate_delay_sec=rate_delay,
            push_delay_sec=push_delay,
        )

        # Server-side version comparison
        update = None
        if app_version and (app.min_version or app.latest_version):
            update_mode = check_update(app_version, app.min_version, app.latest_version)
            if update_mode:
                update = UpdateConfig(
                    min_version=app.min_version,
                    latest_version=app.latest_version,
                    mode=update_mode,
                    appstore_url=app.appstore_url,
                )

        return InitResponse(
            result=offer.url if (app.mode == AppMode.CASINO and offer) else None,
            prompts=prompts,
            update=update,
            icon=icon_name,
        )
