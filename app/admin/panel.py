from pathlib import Path

from starlette.requests import Request
from starlette.responses import Response
from sqlalchemy import create_engine
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette_admin import DropDown
from starlette_admin.contrib.sqlmodel import Admin
from starlette_admin.views import CustomView, Link

from app.admin.auth.provider import CustomAuthProvider

# Import all models BEFORE views to ensure SQLAlchemy relationships are resolved
from app.table.app.model import App  # noqa: F401
from app.table.app_offer_geo.model import AppOfferGeo  # noqa: F401
from app.table.geo.model import Geo  # noqa: F401
from app.table.group.model import Group  # noqa: F401
from app.table.offer.model import Offer  # noqa: F401
from app.table.client.model import Client  # noqa: F401
from app.table.event.model import Event  # noqa: F401
from app.table.init_log.model import InitLog  # noqa: F401

# Path to custom templates
TEMPLATES_DIR = Path(__file__).parent / "templates"


from app.table.app.view import app_view
from app.table.app_offer_geo.view import app_offer_geo_view
from app.table.client.view import client_view
from app.table.event.view import event_view
from app.table.geo.view import geo_view
from app.table.group.view import group_view
from app.table.init_log.view import init_log_view
from app.table.offer.view import offer_view
from config import SETTINGS


def create_admin() -> Admin:
    """Create and configure admin panel."""
    # Create sync engine for starlette-admin
    engine = create_engine(SETTINGS.database_url_sync)

    admin = Admin(
        engine,
        title="Mobile Cloaking",
        base_url="/admin",
        templates_dir=str(TEMPLATES_DIR),
        index_view=CustomView(
            label="Dashboard",
            icon="fas fa-chart-line",
            path="/",
            template_path="dashboard.html",
            add_to_menu=False,
        ),
        auth_provider=CustomAuthProvider(),
        middlewares=[
            Middleware(SessionMiddleware, secret_key=SETTINGS.auth_secret),
        ],
    )

    # Add Dashboard link to menu
    admin.add_view(
        Link(
            label="Dashboard",
            icon="fas fa-chart-line",
            url="/admin",
        )
    )

    # Add views
    admin.add_view(group_view)
    admin.add_view(app_view)
    admin.add_view(offer_view)
    admin.add_view(geo_view)
    admin.add_view(app_offer_geo_view)
    admin.add_view(client_view)
    admin.add_view(event_view)
    admin.add_view(init_log_view)

    # Add documentation links
    admin.add_view(
        DropDown(
            "Documentation",
            icon="fas fa-book",
            views=[
                Link(label="Swagger UI", icon="fas fa-file-code", url="/docs", target="_blank"),
                Link(label="ReDoc", icon="fas fa-file-alt", url="/redoc", target="_blank"),
                Link(label="OpenAPI JSON", icon="fas fa-code", url="/openapi.json", target="_blank"),
            ],
        )
    )

    return admin


def setup_admin(app) -> None:
    """Mount admin panel to the app."""
    admin = create_admin()
    admin.mount_to(app)
