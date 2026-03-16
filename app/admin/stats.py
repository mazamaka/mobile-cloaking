"""Dashboard statistics and data API."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.table.app.enums import AppMode
from app.table.app.model import App
from app.table.client.model import Client
from app.table.geo.model import Geo
from app.table.group.model import Group, GroupType
from app.table.link.model import Link
from app.table.offer.model import Offer
from app.utils.helpers import get_enum_value


async def get_dashboard_stats(session: AsyncSession) -> dict:
    """Get statistics for dashboard."""
    # Apps count
    apps_total = await session.scalar(select(func.count(App.id)))
    apps_casino = await session.scalar(
        select(func.count(App.id)).where(App.mode == AppMode.CASINO)
    )
    apps_native = await session.scalar(
        select(func.count(App.id)).where(App.mode == AppMode.NATIVE)
    )

    # Offers count
    offers_total = await session.scalar(select(func.count(Offer.id)))
    offers_active = await session.scalar(
        select(func.count(Offer.id)).where(Offer.is_active == True)  # noqa: E712
    )

    # Geos count
    geos_total = await session.scalar(select(func.count(Geo.id)))

    # Links count
    links_total = await session.scalar(select(func.count(Link.id)))
    links_active = await session.scalar(
        select(func.count(Link.id)).where(Link.is_active == True)  # noqa: E712
    )

    # Groups count
    groups_app = await session.scalar(
        select(func.count(Group.id)).where(Group.type == GroupType.APP)
    )
    groups_offer = await session.scalar(
        select(func.count(Group.id)).where(Group.type == GroupType.OFFER)
    )

    # Clients count
    clients_total = await session.scalar(select(func.count(Client.id)))

    return {
        "apps": {
            "total": apps_total or 0,
            "casino": apps_casino or 0,
            "native": apps_native or 0,
        },
        "offers": {
            "total": offers_total or 0,
            "active": offers_active or 0,
        },
        "geos": {
            "total": geos_total or 0,
        },
        "links": {
            "total": links_total or 0,
            "active": links_active or 0,
        },
        "groups": {
            "app": groups_app or 0,
            "offer": groups_offer or 0,
        },
        "clients": {
            "total": clients_total or 0,
        },
    }


async def get_apps_list(session: AsyncSession) -> list[dict]:
    """Get all apps for dropdown."""
    stmt = (
        select(App)
        .options(selectinload(App.group))
        .where(App.is_active == True)  # noqa: E712
        .order_by(App.name)
    )
    result = await session.execute(stmt)
    apps = result.scalars().all()

    return [
        {
            "id": app.id,
            "name": app.name or app.bundle_id,
            "bundle_id": app.bundle_id,
            "mode": get_enum_value(app.mode),
            "group": app.group.name if app.group else None,
        }
        for app in apps
    ]


async def get_offers_list(session: AsyncSession) -> list[dict]:
    """Get all offers for dropdown."""
    stmt = (
        select(Offer)
        .options(selectinload(Offer.group))
        .where(Offer.is_active == True)  # noqa: E712
        .order_by(Offer.name)
    )
    result = await session.execute(stmt)
    offers = result.scalars().all()

    return [
        {
            "id": offer.id,
            "name": offer.name,
            "priority": offer.priority,
            "group": offer.group.name if offer.group else None,
        }
        for offer in offers
    ]


async def get_geos_list(session: AsyncSession) -> list[dict]:
    """Get all geos for dropdown."""
    stmt = (
        select(Geo)
        .where(Geo.is_active == True)  # noqa: E712
        .order_by(Geo.is_default.desc(), Geo.code)
    )
    result = await session.execute(stmt)
    geos = result.scalars().all()

    return [
        {
            "id": geo.id,
            "code": geo.code,
            "name": geo.name,
            "is_default": geo.is_default,
        }
        for geo in geos
    ]


async def get_link_matrix(session: AsyncSession) -> list[dict]:
    """Get all Links as matrix data."""
    stmt = (
        select(Link)
        .options(
            selectinload(Link.app),
            selectinload(Link.offer),
            selectinload(Link.geo),
        )
        .order_by(Link.app_id, Link.geo_id)
    )
    result = await session.execute(stmt)
    links = result.scalars().all()

    return [
        {
            "id": link.id,
            "app_id": link.app_id,
            "app_name": link.app.name or link.app.bundle_id if link.app else None,
            "app_mode": get_enum_value(link.app.mode) if link.app else None,
            "offer_id": link.offer_id,
            "offer_name": link.offer.name if link.offer else None,
            "offer_priority": link.offer.priority if link.offer else None,
            "geo_id": link.geo_id,
            "geo_code": link.geo.code if link.geo else None,
            "geo_name": link.geo.name if link.geo else None,
            "geo_is_default": link.geo.is_default if link.geo else False,
            "priority": link.priority,
            "weight": link.weight,
            "is_active": link.is_active,
        }
        for link in links
    ]


async def create_link(
    session: AsyncSession,
    app_id: int,
    offer_id: int,
    geo_id: int,
    priority: int | None = None,
    weight: int | None = None,
) -> dict:
    """Create a new Link."""
    link = Link(
        app_id=app_id,
        offer_id=offer_id,
        geo_id=geo_id,
        priority=priority,
        weight=weight,
        is_active=True,
    )
    session.add(link)
    await session.flush()
    return {"id": link.id, "success": True}


async def delete_link(session: AsyncSession, link_id: int) -> dict:
    """Delete a Link."""
    stmt = select(Link).where(Link.id == link_id)
    result = await session.execute(stmt)
    link = result.scalar_one_or_none()

    if link:
        await session.delete(link)
        return {"success": True}
    return {"success": False, "error": "Link not found"}


async def toggle_link(session: AsyncSession, link_id: int) -> dict:
    """Toggle is_active status of a Link."""
    stmt = select(Link).where(Link.id == link_id)
    result = await session.execute(stmt)
    link = result.scalar_one_or_none()

    if link:
        link.is_active = not link.is_active
        return {"success": True, "is_active": link.is_active}
    return {"success": False, "error": "Link not found"}


async def get_groups_list(
    session: AsyncSession, group_type: GroupType | None = None
) -> list[dict]:
    """Get groups for dropdown."""
    stmt = select(Group).where(Group.is_active == True)  # noqa: E712
    if group_type:
        stmt = stmt.where(Group.type == group_type)
    stmt = stmt.order_by(Group.name)

    result = await session.execute(stmt)
    groups = result.scalars().all()

    return [
        {
            "id": group.id,
            "name": group.name,
            "type": get_enum_value(group.type),
        }
        for group in groups
    ]


async def create_app(
    session: AsyncSession,
    bundle_id: str,
    name: str | None = None,
    apple_id: str | None = None,
    mode: str = "native",
    group_id: int | None = None,
) -> dict:
    """Create a new App."""
    # Check if bundle_id already exists
    stmt = select(App).where(App.bundle_id == bundle_id)
    result = await session.execute(stmt)
    if result.scalar_one_or_none():
        return {"success": False, "error": "Bundle ID already exists"}

    app = App(
        bundle_id=bundle_id,
        name=name or bundle_id,
        apple_id=apple_id,
        mode=AppMode(mode),
        group_id=group_id,
    )
    session.add(app)
    await session.flush()
    return {"success": True, "id": app.id, "name": app.name}


async def create_offer(
    session: AsyncSession,
    name: str,
    url: str,
    priority: int = 0,
    weight: int = 100,
    group_id: int | None = None,
) -> dict:
    """Create a new Offer."""
    offer = Offer(
        name=name,
        url=url,
        priority=priority,
        weight=weight,
        group_id=group_id,
    )
    session.add(offer)
    await session.flush()
    return {"success": True, "id": offer.id, "name": offer.name}


async def create_geo(
    session: AsyncSession,
    code: str,
    name: str,
    is_default: bool = False,
) -> dict:
    """Create a new Geo."""
    # Check if code already exists
    stmt = select(Geo).where(Geo.code == code)
    result = await session.execute(stmt)
    if result.scalar_one_or_none():
        return {"success": False, "error": "Geo code already exists"}

    geo = Geo(
        code=code.upper(),
        name=name,
        is_default=is_default,
    )
    session.add(geo)
    await session.flush()
    return {"success": True, "id": geo.id, "code": geo.code}


async def get_events_stats(session: AsyncSession) -> dict:
    """Get events statistics for dashboard."""
    from datetime import timedelta

    from app.table.event.model import Event
    from app.utils.helpers import utc_now

    now = utc_now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)

    events_today = (
        await session.scalar(
            select(func.count(Event.id)).where(Event.received_at >= today_start)
        )
        or 0
    )

    events_week = (
        await session.scalar(
            select(func.count(Event.id)).where(Event.received_at >= week_ago)
        )
        or 0
    )

    events_month = (
        await session.scalar(
            select(func.count(Event.id)).where(Event.received_at >= month_ago)
        )
        or 0
    )

    events_total = await session.scalar(select(func.count(Event.id))) or 0

    # Top events by name
    top_events_stmt = (
        select(Event.name, func.count(Event.id).label("count"))
        .where(Event.received_at >= week_ago)
        .group_by(Event.name)
        .order_by(func.count(Event.id).desc())
        .limit(5)
    )
    result = await session.execute(top_events_stmt)
    top_events = [{"name": row[0], "count": row[1]} for row in result.all()]

    # Clients stats
    clients_today = (
        await session.scalar(
            select(func.count(Client.id)).where(Client.first_seen_at >= today_start)
        )
        or 0
    )

    clients_week = (
        await session.scalar(
            select(func.count(Client.id)).where(Client.first_seen_at >= week_ago)
        )
        or 0
    )

    clients_with_push = (
        await session.scalar(
            select(func.count(Client.id)).where(
                Client.push_token.isnot(None)  # type: ignore[union-attr]
            )
        )
        or 0
    )

    return {
        "events": {
            "today": events_today,
            "week": events_week,
            "month": events_month,
            "total": events_total,
            "top": top_events,
        },
        "clients": {
            "new_today": clients_today,
            "new_week": clients_week,
            "with_push": clients_with_push,
        },
    }
