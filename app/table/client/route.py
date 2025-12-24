from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import RequestHeaders, get_db, get_headers
from app.table.client.schemas import InitRequest
from app.table.client.service import InitService

router = APIRouter(prefix="/client", tags=["client"])


@router.post("/init")
async def client_init(
    body: InitRequest,
    headers: RequestHeaders = Depends(get_headers),
    session: AsyncSession = Depends(get_db),
) -> JSONResponse:
    """
    Initialize client session.

    Returns:
        200 OK - Native mode (show game/app)
        400 Bad Request - Casino mode (open WebView with result URL)
    """
    service = InitService(session)
    status_code, response = await service.process_init(body)

    return JSONResponse(
        status_code=status_code,
        content=response.model_dump(exclude_none=True),
    )
