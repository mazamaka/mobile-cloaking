from fastapi import APIRouter

from app.table.client.route import router as client_router
from app.table.event.route import router as event_router

router = APIRouter(prefix="/api/v1")

router.include_router(client_router)
router.include_router(event_router)
