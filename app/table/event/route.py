from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import RequestHeaders, get_db, get_headers
from app.table.event.schemas import EventRequest, EventResponse
from app.table.event.service import EventService

router = APIRouter(prefix="/client", tags=["client"])


@router.post("/event", response_model=EventResponse)
async def client_event(
    body: EventRequest,
    headers: RequestHeaders = Depends(get_headers),
    session: AsyncSession = Depends(get_db),
) -> EventResponse:
    """
    Log client event (Rate Us, Push prompts, etc.)

    Returns empty object on success.
    """
    service = EventService(session)
    await service.process_event(body)

    return EventResponse()
