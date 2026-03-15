from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import RequestHeaders, get_db, get_headers
from app.ratelimit import limiter
from app.table.client.schemas import InitRequest, InitResponse
from app.table.client.service import InitService

router = APIRouter(prefix="/client", tags=["client"])


@router.post(
    "/init",
    summary="Инициализация клиента",
    description="""
## Инициализация клиента при запуске приложения

Этот эндпоинт — главная точка входа для iOS-приложения.
Вызывается **один раз при каждом запуске** приложения.

### Логика работы
1. Приложение отправляет данные об устройстве и пользователе
2. Сервер определяет режим работы на основе настроек приложения в админке
3. Возвращает ответ с конфигурацией

### Определение режима по ответу

| Поле `result` | Режим | Действие |
|---------------|-------|----------|
| `null` | Native | Показать легальное приложение/игру |
| URL строка | Casino | Открыть WebView с указанным URL |

### Заголовки запроса
| Header | Обязательный | Описание |
|--------|--------------|----------|
| `X-Schema` | Да | Версия схемы API (сейчас: `1`) |
| `X-App-Bundle-Id` | Нет | Bundle ID приложения (fallback) |
| `X-App-Version` | Нет | Версия приложения (fallback) |
| `X-API-Key` | Нет | Ключ авторизации (если настроен) |
    """,
    response_model=InitResponse,
    responses={
        200: {
            "description": "Конфигурация клиента",
            "content": {
                "application/json": {
                    "examples": {
                        "native": {
                            "summary": "Native режим",
                            "description": "result=null — показать нативное приложение",
                            "value": {
                                "result": None,
                                "prompts": {
                                    "rate_delay_sec": 180,
                                    "push_delay_sec": 60,
                                },
                                "update": {
                                    "min_version": "1.0",
                                    "latest_version": "1.2",
                                    "mode": "soft",
                                    "appstore_url": "itms-apps://itunes.apple.com/app/id123456789",
                                },
                                "icon": None,
                            },
                        },
                        "casino": {
                            "summary": "Casino режим",
                            "description": "result=URL — открыть WebView",
                            "value": {
                                "result": "https://casino-partner.com/?click_id=abc123",
                                "prompts": {
                                    "rate_delay_sec": 180,
                                    "push_delay_sec": 60,
                                },
                                "update": None,
                                "icon": "icon_bonus",
                            },
                        },
                    }
                }
            },
        },
        401: {"description": "Неверный API ключ (X-API-Key)"},
        404: {"description": "Приложение не найдено по bundle_id"},
        422: {"description": "Ошибка валидации — неверный формат данных"},
        429: {"description": "Превышен лимит запросов"},
    },
)
@limiter.limit("60/minute")
async def client_init(
    request: Request,
    body: InitRequest,
    headers: RequestHeaders = Depends(get_headers),
    session: AsyncSession = Depends(get_db),
) -> InitResponse:
    """Инициализация клиента при запуске приложения."""
    service = InitService(session)
    return await service.process_init(body, api_key=headers.api_key)
