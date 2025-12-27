from fastapi import APIRouter

from app.api.v1.dashboard import router as dashboard_router
from app.table.client.route import router as client_router
from app.table.event.route import router as event_router

router = APIRouter(prefix="/api/v1")

router.include_router(client_router)
router.include_router(event_router)
router.include_router(dashboard_router)
