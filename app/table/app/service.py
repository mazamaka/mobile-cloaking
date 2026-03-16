"""Service for App registration."""

import uuid

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.table.app.enums import AppMode
from app.table.app.model import App
from app.table.app.schemas import AppRegisterRequest, AppRegisterResponse
from app.table.geo.model import Geo
from app.table.group.model import Group, GroupType
from app.table.link.model import Link
from app.table.offer.model import Offer
from app.utils.logger import logger


class AppRegistrationService:
    """Handle app registration: create App + optional Link bindings."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def register(self, req: AppRegisterRequest) -> AppRegisterResponse:
        """Register a new app with optional offer-geo bindings.

        Args:
            req: Registration request with app data and optional offers.

        Returns:
            Registration result with app_id, api_key, and warnings.

        Raises:
            HTTPException: 409 if bundle_id already exists.
        """
        warnings: list[str] = []

        # 1. Check duplicate bundle_id
        stmt = select(App).where(App.bundle_id == req.bundle_id)
        result = await self.session.execute(stmt)
        if result.scalar_one_or_none() is not None:
            raise HTTPException(
                status_code=409,
                detail=f"App with bundle_id '{req.bundle_id}' already exists",
            )

        # 2. Resolve group
        group_id: int | None = None
        if req.group_name:
            stmt = select(Group).where(
                Group.name == req.group_name,
                Group.type == GroupType.APP,
            )
            result = await self.session.execute(stmt)
            group = result.scalar_one_or_none()
            if group:
                group_id = group.id
            else:
                warnings.append(
                    f"Group '{req.group_name}' (type=app) not found, app created without group"
                )

        # 3. Auto-generate api_key if not provided
        api_key = req.api_key or str(uuid.uuid4())

        # 4. Create App
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

        # 5. Create links if offers provided and mode=casino
        links_created = 0
        if req.offers and req.mode == "casino":
            links_created = await self._create_links(app, req, warnings)
        elif req.offers and req.mode == "native":
            warnings.append(
                "Offers ignored: mode is 'native', links only created for 'casino'"
            )

        # 6. Commit
        await self.session.commit()

        logger.info(
            f"App registered: bundle_id={req.bundle_id}, "
            f"mode={req.mode}, links={links_created}"
        )

        # 7. Return response
        return AppRegisterResponse(
            app_id=app.id,  # type: ignore[arg-type]  # id is set after flush
            bundle_id=app.bundle_id,
            api_key=app.api_key,
            mode=req.mode,
            links_created=links_created,
            warnings=warnings,
        )

    async def _create_links(
        self,
        app: App,
        req: AppRegisterRequest,
        warnings: list[str],
    ) -> int:
        """Create Link records for offer-geo bindings.

        Returns:
            Number of links successfully created.
        """
        links_created = 0

        for binding in req.offers or []:
            # Find offer by name
            stmt = select(Offer).where(Offer.name == binding.offer_name)
            result = await self.session.execute(stmt)
            offer = result.scalar_one_or_none()
            if not offer:
                warnings.append(f"Offer '{binding.offer_name}' not found, skipped")
                continue

            # Find geo by code
            stmt = select(Geo).where(Geo.code == binding.geo_code)
            result = await self.session.execute(stmt)
            geo = result.scalar_one_or_none()
            if not geo:
                warnings.append(f"Geo '{binding.geo_code}' not found, skipped")
                continue

            link = Link(
                app_id=app.id,  # type: ignore[arg-type]  # id is set after flush
                offer_id=offer.id,  # type: ignore[arg-type]
                geo_id=geo.id,  # type: ignore[arg-type]
                priority=binding.priority,
                weight=binding.weight,
            )
            self.session.add(link)
            links_created += 1

        return links_created
