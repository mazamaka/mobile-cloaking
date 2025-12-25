from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import RequestHeaders, get_db, get_headers
from app.table.client.schemas import InitRequest, InitResponseCasino, InitResponseNative
from app.table.client.service import InitService

router = APIRouter(prefix="/client", tags=["client"])


@router.post(
    "/init",
    summary="Инициализация клиента",
    description="""
## 🚀 Инициализация клиента при запуске приложения

Этот эндпоинт — главная точка входа ("фейс-контроль") для iOS-приложения.
Вызывается **один раз при каждом запуске** приложения.

### Логика работы
1. Приложение отправляет данные об устройстве и пользователе
2. Сервер определяет режим работы на основе настроек приложения в админке
3. Возвращает соответствующий ответ

### Режимы ответа

#### ✅ 200 OK — Native режим
Показываем легальное приложение/игру. Используется при:
- Проверке модератором Apple
- Когда приложение настроено в режим "native"

#### ❌ 400 Bad Request — Casino режим
Открываем WebView с URL казино. Поле `result` содержит URL для открытия.

### Заголовки запроса
| Header | Обязательный | Описание |
|--------|--------------|----------|
| `X-Schema` | Да | Версия схемы API (сейчас: `1`) |
| `X-App-Bundle-Id` | Нет | Bundle ID приложения (fallback) |
| `X-App-Version` | Нет | Версия приложения (fallback) |

### Что происходит на сервере
1. Создаётся или обновляется запись клиента в БД
2. Логируется запрос в `init_logs`
3. Возвращается конфигурация prompts и обновлений
    """,
    responses={
        200: {
            "description": "Native режим — показать легальное приложение",
            "model": InitResponseNative,
            "content": {
                "application/json": {
                    "example": {
                        "prompts": {
                            "rate_delay_sec": 180,
                            "push_delay_sec": 60
                        },
                        "update": {
                            "min_version": "1.0",
                            "latest_version": "1.2",
                            "mode": "soft",
                            "appstore_url": "itms-apps://itunes.apple.com/app/id123456789"
                        }
                    }
                }
            }
        },
        400: {
            "description": "Casino режим — открыть WebView с URL казино",
            "model": InitResponseCasino,
            "content": {
                "application/json": {
                    "example": {
                        "result": "https://casino-partner.com/?click_id=abc123",
                        "prompts": {
                            "rate_delay_sec": 180,
                            "push_delay_sec": 60
                        },
                        "update": None
                    }
                }
            }
        },
        422: {
            "description": "Ошибка валидации — неверный формат данных"
        }
    }
)
async def client_init(
    body: InitRequest,
    headers: RequestHeaders = Depends(get_headers),
    session: AsyncSession = Depends(get_db),
) -> JSONResponse:
    """
    Инициализация клиента при запуске приложения.

    Определяет режим работы (native/casino) и возвращает конфигурацию.
    """
    service = InitService(session)
    status_code, response = await service.process_init(body)

    return JSONResponse(
        status_code=status_code,
        content=response.model_dump(exclude_none=True),
    )
