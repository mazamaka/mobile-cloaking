from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import RequestHeaders, get_db, get_headers
from app.ratelimit import limiter
from app.table.event.schemas import EventRequest, EventResponse
from app.table.event.service import EventService

router = APIRouter(prefix="/client", tags=["client"])


@router.post(
    "/event",
    response_model=EventResponse,
    summary="Логирование события",
    description="""
## Логирование событий от клиента

Эндпоинт для отправки аналитических событий с мобильного приложения.
Используется для отслеживания взаимодействия пользователя с UI-элементами.

### Типы событий

#### Rate Us (оценка приложения)
| Событие | Описание |
|---------|----------|
| `rate_sheet_shown` | Показан popup "Оцените приложение" |
| `rate_slider_completed` | Пользователь выставил оценку |
| `rate_sheet_closed` | Закрыл popup без действия |

#### Push-уведомления
| Событие | Описание |
|---------|----------|
| `push_prompt_shown` | Показан запрос на push-уведомления |
| `push_prompt_accepted` | Пользователь разрешил push |
| `push_prompt_declined` | Пользователь отклонил push |

#### Иконки
| Событие | Описание |
|---------|----------|
| `icon_banner_shown` | Показан баннер смены иконки |
| `icon_swipe_completed` | Иконка изменена |
| `icon_banner_expired` | Баннер истёк |

### Поле `props`
Дополнительные данные события в формате JSON-объекта.

### Заголовки запроса
| Header | Обязательный | Описание |
|--------|--------------|----------|
| `X-Schema` | Да | Версия схемы API (сейчас: `1`) |
| `X-App-Bundle-Id` | Нет | Bundle ID приложения |
| `X-App-Version` | Нет | Версия приложения |

### Важно
- Поле `ts` — это Unix timestamp в **секундах** (время на устройстве)
- События привязываются к клиенту по `internal_id`
- Неизвестные события сохраняются как есть
    """,
    responses={
        200: {
            "description": "Событие успешно записано",
            "content": {"application/json": {"example": {}}},
        },
        422: {"description": "Ошибка валидации — неверный формат данных"},
        429: {"description": "Превышен лимит запросов"},
    },
)
@limiter.limit("120/minute")
async def client_event(
    request: Request,
    body: EventRequest,
    headers: RequestHeaders = Depends(get_headers),
    session: AsyncSession = Depends(get_db),
) -> EventResponse:
    """Логирование события от клиента."""
    service = EventService(session)
    await service.process_event(body)
    return EventResponse()
