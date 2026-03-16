"""Service for App management."""

import uuid
from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.cache.redis import cache
from app.table.app.enums import AppMode
from app.table.app.model import App
from app.table.app.schemas import (
    AppAddLinkRequest,
    AppAddLinkResponse,
    AppBulkModeRequest,
    AppBulkModeResponse,
    AppDetailResponse,
    AppListResponse,
    AppModeRequest,
    AppModeResponse,
    AppRegisterRequest,
    AppRegisterResponse,
    AppUpdateRequest,
    MessageResponse,
    TestInitResponse,
)
from app.table.geo.model import Geo
from app.table.group.model import Group, GroupType
from app.table.link.model import Link
from app.table.offer.model import Offer
from app.utils.logger import logger


class AppService:
    """Handle all app management operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # --- Helpers ---

    async def _get_app_or_404(self, bundle_id: str) -> App:
        """Get app by bundle_id or raise 404."""
        stmt = select(App).where(App.bundle_id == bundle_id)
        result = await self.session.execute(stmt)
        app = result.scalar_one_or_none()
        if not app:
            raise HTTPException(status_code=404, detail=f"App '{bundle_id}' not found")
        return app

    async def _resolve_group(self, group_name: str) -> tuple[int | None, str | None]:
        """Resolve group by name. Returns (group_id, warning)."""
        stmt = select(Group).where(
            Group.name == group_name, Group.type == GroupType.APP
        )
        result = await self.session.execute(stmt)
        group = result.scalar_one_or_none()
        if group:
            return group.id, None
        return None, f"Group '{group_name}' (type=app) not found"

    def _app_to_detail(self, app: App) -> AppDetailResponse:
        """Convert App model to detail response."""
        return AppDetailResponse(
            id=app.id,  # type: ignore[arg-type]
            bundle_id=app.bundle_id,
            apple_id=app.apple_id,
            name=app.name,
            api_key=app.api_key,
            group_id=app.group_id,
            mode=app.mode.value if isinstance(app.mode, AppMode) else str(app.mode),
            rate_delay_sec=app.rate_delay_sec,
            push_delay_sec=app.push_delay_sec,
            min_version=app.min_version,
            latest_version=app.latest_version,
            update_mode=app.update_mode.value if app.update_mode else None,
            appstore_url=app.appstore_url,
            icon_name=app.icon_name,
            is_active=app.is_active,
            links_count=len(app.links) if app.links else 0,
        )

    # --- Registration ---

    async def register(self, req: AppRegisterRequest) -> AppRegisterResponse:
        """Register a new app with optional offer-geo bindings."""
        warnings: list[str] = []

        # Check duplicate
        stmt = select(App).where(App.bundle_id == req.bundle_id)
        result = await self.session.execute(stmt)
        if result.scalar_one_or_none() is not None:
            raise HTTPException(
                status_code=409,
                detail=f"App with bundle_id '{req.bundle_id}' already exists",
            )

        # Resolve group
        group_id: int | None = None
        if req.group_name:
            group_id, warning = await self._resolve_group(req.group_name)
            if warning:
                warnings.append(warning)

        api_key = req.api_key or str(uuid.uuid4())

        app = App(
            bundle_id=req.bundle_id,
            name=req.name,
            apple_id=req.apple_id,
            mode=AppMode(req.mode),
            api_key=api_key,
            group_id=group_id,
        )
        self.session.add(app)
        await self.session.flush()

        links_created = 0
        if req.offers and req.mode == "casino":
            links_created = await self._create_links(app, req, warnings)
        elif req.offers and req.mode == "native":
            warnings.append(
                "Offers ignored: mode is 'native', links only created for 'casino'"
            )

        await self.session.commit()

        logger.info(
            f"App registered: bundle_id={req.bundle_id}, "
            f"mode={req.mode}, links={links_created}"
        )

        return AppRegisterResponse(
            app_id=app.id,  # type: ignore[arg-type]
            bundle_id=app.bundle_id,
            api_key=app.api_key,
            mode=req.mode,
            links_created=links_created,
            warnings=warnings,
        )

    async def _create_links(
        self, app: App, req: AppRegisterRequest, warnings: list[str]
    ) -> int:
        """Create Link records for offer-geo bindings."""
        links_created = 0
        for binding in req.offers or []:
            stmt = select(Offer).where(Offer.name == binding.offer_name)
            result = await self.session.execute(stmt)
            offer = result.scalar_one_or_none()
            if not offer:
                warnings.append(f"Offer '{binding.offer_name}' not found, skipped")
                continue

            stmt = select(Geo).where(Geo.code == binding.geo_code)
            result = await self.session.execute(stmt)
            geo = result.scalar_one_or_none()
            if not geo:
                warnings.append(f"Geo '{binding.geo_code}' not found, skipped")
                continue

            link = Link(
                app_id=app.id,  # type: ignore[arg-type]
                offer_id=offer.id,  # type: ignore[arg-type]
                geo_id=geo.id,  # type: ignore[arg-type]
                priority=binding.priority,
                weight=binding.weight,
            )
            self.session.add(link)
            links_created += 1
        return links_created

    # --- Get ---

    async def get_detail(self, bundle_id: str) -> AppDetailResponse:
        """Get app details by bundle_id."""
        app = await self._get_app_or_404(bundle_id)
        return self._app_to_detail(app)

    # --- List ---

    async def list_apps(
        self,
        mode: str | None = None,
        is_active: bool | None = None,
        group_id: int | None = None,
    ) -> AppListResponse:
        """List apps with optional filters."""
        stmt = select(App)
        if mode:
            stmt = stmt.where(App.mode == AppMode(mode))
        if is_active is not None:
            stmt = stmt.where(App.is_active == is_active)
        if group_id is not None:
            stmt = stmt.where(App.group_id == group_id)
        stmt = stmt.order_by(App.id.desc())

        result = await self.session.execute(stmt)
        apps = result.scalars().all()

        return AppListResponse(
            items=[self._app_to_detail(a) for a in apps],
            total=len(apps),
        )

    # --- Update ---

    async def update(self, bundle_id: str, req: AppUpdateRequest) -> AppDetailResponse:
        """Update app fields."""
        app = await self._get_app_or_404(bundle_id)

        if req.name is not None:
            app.name = req.name
        if req.apple_id is not None:
            app.apple_id = req.apple_id
        if req.mode is not None:
            app.mode = AppMode(req.mode)
        if req.api_key is not None:
            app.api_key = req.api_key
        if req.rate_delay_sec is not None:
            app.rate_delay_sec = req.rate_delay_sec
        if req.push_delay_sec is not None:
            app.push_delay_sec = req.push_delay_sec
        if req.min_version is not None:
            app.min_version = req.min_version
        if req.latest_version is not None:
            app.latest_version = req.latest_version
        if req.update_mode is not None:
            app.update_mode = req.update_mode
        if req.appstore_url is not None:
            app.appstore_url = req.appstore_url
        if req.icon_name is not None:
            app.icon_name = req.icon_name
        if req.is_active is not None:
            app.is_active = req.is_active
        if req.group_name is not None:
            group_id, _ = await self._resolve_group(req.group_name)
            app.group_id = group_id

        app.updated_at = datetime.utcnow()
        await self.session.commit()

        # Invalidate cache
        await cache.invalidate_app(bundle_id)

        return self._app_to_detail(app)

    # --- Mode switch ---

    async def switch_mode(self, bundle_id: str, req: AppModeRequest) -> AppModeResponse:
        """Quick mode switch for a single app."""
        app = await self._get_app_or_404(bundle_id)
        old_mode = app.mode.value if isinstance(app.mode, AppMode) else str(app.mode)
        app.mode = AppMode(req.mode)
        app.updated_at = datetime.utcnow()
        await self.session.commit()
        await cache.invalidate_app(bundle_id)

        logger.info(f"Mode switch: {bundle_id} {old_mode} -> {req.mode}")

        return AppModeResponse(
            bundle_id=bundle_id, old_mode=old_mode, new_mode=req.mode
        )

    # --- Bulk mode ---

    async def bulk_mode(self, req: AppBulkModeRequest) -> AppBulkModeResponse:
        """Mass mode switch for multiple apps."""
        updated = 0
        not_found: list[str] = []

        for bid in req.bundle_ids:
            stmt = select(App).where(App.bundle_id == bid)
            result = await self.session.execute(stmt)
            app = result.scalar_one_or_none()
            if not app:
                not_found.append(bid)
                continue
            app.mode = AppMode(req.mode)
            app.updated_at = datetime.utcnow()
            updated += 1

        await self.session.commit()

        # Invalidate cache for all updated apps
        for bid in req.bundle_ids:
            if bid not in not_found:
                await cache.invalidate_app(bid)

        logger.info(f"Bulk mode switch: {updated} apps -> {req.mode}")

        return AppBulkModeResponse(updated=updated, not_found=not_found)

    # --- Soft delete ---

    async def soft_delete(self, bundle_id: str) -> MessageResponse:
        """Deactivate app (soft delete)."""
        app = await self._get_app_or_404(bundle_id)
        app.is_active = False
        app.updated_at = datetime.utcnow()
        await self.session.commit()
        await cache.invalidate_app(bundle_id)

        return MessageResponse(message=f"App '{bundle_id}' deactivated")

    # --- Add link ---

    async def add_link(
        self, bundle_id: str, req: AppAddLinkRequest
    ) -> AppAddLinkResponse:
        """Add a link (offer+geo) to an existing app."""
        app = await self._get_app_or_404(bundle_id)

        stmt = select(Offer).where(Offer.name == req.offer_name)
        result = await self.session.execute(stmt)
        offer = result.scalar_one_or_none()
        if not offer:
            raise HTTPException(
                status_code=404, detail=f"Offer '{req.offer_name}' not found"
            )

        stmt = select(Geo).where(Geo.code == req.geo_code)
        result = await self.session.execute(stmt)
        geo = result.scalar_one_or_none()
        if not geo:
            raise HTTPException(
                status_code=404, detail=f"Geo '{req.geo_code}' not found"
            )

        # Check duplicate
        stmt = select(Link).where(Link.app_id == app.id, Link.geo_id == geo.id)
        result = await self.session.execute(stmt)
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=409,
                detail=f"Link for geo '{req.geo_code}' already exists in this app",
            )

        link = Link(
            app_id=app.id,  # type: ignore[arg-type]
            offer_id=offer.id,  # type: ignore[arg-type]
            geo_id=geo.id,  # type: ignore[arg-type]
            priority=req.priority,
            weight=req.weight,
        )
        self.session.add(link)
        await self.session.commit()

        return AppAddLinkResponse(
            link_id=link.id,  # type: ignore[arg-type]
            app_id=app.id,  # type: ignore[arg-type]
            offer_id=offer.id,  # type: ignore[arg-type]
            geo_id=geo.id,  # type: ignore[arg-type]
        )

    # --- Test init (dry run) ---

    async def test_init(self, bundle_id: str, geo: str) -> TestInitResponse:
        """Dry-run init: show what would be returned for a given geo."""
        app = await self._get_app_or_404(bundle_id)
        mode_str = app.mode.value if isinstance(app.mode, AppMode) else str(app.mode)

        if mode_str == "native":
            return TestInitResponse(mode=mode_str, would_return=None)

        # Try exact geo match
        stmt = (
            select(Offer, Geo)
            .join(Link, Offer.id == Link.offer_id)
            .join(Geo, Link.geo_id == Geo.id)
            .where(
                Link.app_id == app.id,
                Link.is_active == True,  # noqa: E712
                Offer.is_active == True,  # noqa: E712
                Geo.is_active == True,  # noqa: E712
                Geo.code == geo,
            )
            .order_by(func.coalesce(Link.priority, Offer.priority).desc())
            .limit(1)
        )
        result = await self.session.execute(stmt)
        row = result.first()

        if row:
            return TestInitResponse(
                mode=mode_str,
                would_return=row[0].url,
                offer_name=row[0].name,
                geo_code=geo,
                geo_matched="exact",
            )

        # Try default geo
        stmt = (
            select(Offer, Geo)
            .join(Link, Offer.id == Link.offer_id)
            .join(Geo, Link.geo_id == Geo.id)
            .where(
                Link.app_id == app.id,
                Link.is_active == True,  # noqa: E712
                Offer.is_active == True,  # noqa: E712
                Geo.is_active == True,  # noqa: E712
                Geo.is_default == True,  # noqa: E712
            )
            .order_by(func.coalesce(Link.priority, Offer.priority).desc())
            .limit(1)
        )
        result = await self.session.execute(stmt)
        row = result.first()

        if row:
            return TestInitResponse(
                mode=mode_str,
                would_return=row[0].url,
                offer_name=row[0].name,
                geo_code=row[1].code,
                geo_matched="default",
            )

        return TestInitResponse(mode=mode_str, would_return=None)
