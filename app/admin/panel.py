from sqlalchemy import create_engine
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette_admin import DropDown
from starlette_admin.contrib.sqlmodel import Admin
from starlette_admin.views import Link

from app.admin.auth.provider import CustomAuthProvider
from app.table.app.view import app_view
from app.table.client.view import client_view
from app.table.event.view import event_view
from app.table.geo.view import geo_view
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
        auth_provider=CustomAuthProvider(),
        middlewares=[
            Middleware(SessionMiddleware, secret_key=SETTINGS.auth_secret),
        ],
    )

    # Add views
    admin.add_view(app_view)
    admin.add_view(geo_view)
    admin.add_view(offer_view)
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
