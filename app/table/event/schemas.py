from typing import Any

from pydantic import BaseModel, Field


class EventAppInfo(BaseModel):
    """Информация о приложении для события."""

    bundle_id: str = Field(
        ...,
        description="Bundle ID приложения",
        examples=["com.example.game"],
    )
    version: str = Field(
        ...,
        description="Версия приложения",
        examples=["1.0.0"],
    )


class EventIdsInfo(BaseModel):
    """Идентификаторы для привязки события."""

    internal_id: str = Field(
        ...,
        description="Уникальный ID устройства (UUID v4 из Keychain)",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )


class EventData(BaseModel):
    """Данные события."""

    name: str = Field(
        ...,
        description="""Название события. Поддерживаемые типы:
- `rate_sheet_shown` — показан popup оценки
- `rate_slider_completed` — пользователь оценил
- `rate_sheet_closed` — закрыл popup
- `push_prompt_shown` — показан запрос push
- `push_prompt_accepted` — разрешил push
- `push_prompt_declined` — отклонил push""",
        examples=["rate_sheet_shown", "push_prompt_accepted"],
    )
    ts: int = Field(
        ...,
        description="Unix timestamp события в секундах (время на устройстве)",
        examples=[1734541234],
    )
    props: dict[str, Any] | None = Field(
        default=None,
        description="Дополнительные свойства события (произвольный JSON)",
        examples=[{"rating": 5}, {"source": "settings"}],
    )


class EventRequest(BaseModel):
    """
    Тело запроса POST /api/v1/client/event.

    Отправляется при каждом значимом действии пользователя.
    """

    schema_: int = Field(
        alias="schema",
        description="Версия схемы API (сейчас всегда 1)",
        examples=[1],
    )
    app: EventAppInfo = Field(
        ...,
        description="Информация о приложении",
    )
    ids: EventIdsInfo = Field(
        ...,
        description="Идентификаторы устройства",
    )
    event: EventData = Field(
        ...,
        description="Данные события",
    )

    model_config = {"extra": "ignore", "populate_by_name": True}


class EventResponse(BaseModel):
    """
    Ответ на событие — пустой объект.

    При успешной записи возвращается `{}`.
    """

    pass
