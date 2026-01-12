from pydantic import BaseModel, Field

from app.schemas.common import ATTStatus
from app.table.app.enums import UpdateMode


# Request schemas
class AppInfo(BaseModel):
    """Информация о приложении."""

    bundle_id: str = Field(
        ...,
        description="Bundle ID приложения (например: com.company.app)",
        examples=["com.example.game"],
    )
    version: str = Field(
        ...,
        description="Версия приложения",
        examples=["1.0.0", "2.1.3"],
    )


class DeviceInfo(BaseModel):
    """Информация об устройстве."""

    language: str = Field(
        ...,
        description="Язык устройства в формате ISO (например: en-US, ru-RU)",
        examples=["en-US", "ru-RU", "en-EE"],
    )
    timezone: str = Field(
        ...,
        description="Часовой пояс устройства",
        examples=["Europe/Moscow", "Europe/Budapest", "America/New_York"],
    )
    region: str = Field(
        ...,
        description="Регион устройства (ISO 3166-1 alpha-2)",
        examples=["RU", "EE", "HU", "US"],
    )


class PrivacyInfo(BaseModel):
    """Настройки приватности."""

    att: ATTStatus = Field(
        ...,
        description="""Статус App Tracking Transparency (iOS 14+):
- `authorized` — пользователь разрешил трекинг
- `denied` — пользователь запретил трекинг
- `notDetermined` — пользователь ещё не принял решение
- `restricted` — трекинг ограничен (родительский контроль)
- `legacy` — iOS версия ниже 14
- `unavailable` — трекинг отключён на устройстве""",
    )


class IdsInfo(BaseModel):
    """Идентификаторы устройства."""

    internal_id: str = Field(
        ...,
        description="Уникальный ID устройства (UUID v4, хранится в Keychain)",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    idfa: str | None = Field(
        default=None,
        description="IDFA (Identifier for Advertisers). Доступен только при att=authorized",
        examples=["AEBE52E7-03EE-455A-B3C4-E57283966239"],
    )


class AttributionInfo(BaseModel):
    """Данные атрибуции."""

    appsflyer_id: str | None = Field(
        default=None,
        description="AppsFlyer ID для атрибуции установок",
        examples=["1765992827433-2791097"],
    )


class PushInfo(BaseModel):
    """Push-уведомления."""

    token: str | None = Field(
        default=None,
        description="Push-токен устройства (APNs token)",
        examples=["abc123def456..."],
    )


class InitRequest(BaseModel):
    """
    Тело запроса POST /api/v1/client/init.

    Отправляется при каждом запуске приложения для определения режима работы.
    """

    schema_: int = Field(
        alias="schema",
        description="Версия схемы API (сейчас всегда 1)",
        examples=[1],
    )
    app: AppInfo = Field(
        ...,
        description="Информация о приложении",
    )
    device: DeviceInfo = Field(
        ...,
        description="Информация об устройстве",
    )
    privacy: PrivacyInfo = Field(
        ...,
        description="Настройки приватности (ATT статус)",
    )
    ids: IdsInfo = Field(
        ...,
        description="Идентификаторы устройства",
    )
    attribution: AttributionInfo | None = Field(
        default=None,
        description="Данные атрибуции (опционально)",
    )
    push: PushInfo | None = Field(
        default=None,
        description="Push-токен (опционально)",
    )

    model_config = {"extra": "ignore", "populate_by_name": True}


# Response schemas
class PromptsConfig(BaseModel):
    """Настройки всплывающих окон."""

    rate_delay_sec: int = Field(
        ...,
        description="Задержка перед показом 'Оцените приложение' (секунды)",
        examples=[180],
    )
    push_delay_sec: int = Field(
        ...,
        description="Задержка перед показом запроса push-уведомлений (секунды)",
        examples=[60],
    )


class UpdateConfig(BaseModel):
    """Настройки обновления приложения."""

    min_version: str | None = Field(
        default=None,
        description="Минимальная поддерживаемая версия",
        examples=["1.0.0"],
    )
    latest_version: str | None = Field(
        default=None,
        description="Последняя доступная версия",
        examples=["1.2.0"],
    )
    mode: UpdateMode | None = Field(
        default=None,
        description="Режим обновления: soft (рекомендуем) или force (обязательно)",
    )
    appstore_url: str | None = Field(
        default=None,
        description="URL для открытия App Store",
        examples=["itms-apps://itunes.apple.com/app/id123456789"],
    )


class InitResponse(BaseModel):
    """
    Ответ 200 OK на /client/init.

    Режим определяется по наличию поля `result`:
    - `result` есть → Casino режим (открыть WebView с URL)
    - `result` отсутствует → Native режим (показать нативный контент)
    """

    result: str | None = Field(
        default=None,
        description="URL казино для открытия в WebView. Если null — показать нативный контент.",
        examples=["https://casino-partner.com/?click_id=abc123&sub1=value"],
    )
    prompts: PromptsConfig = Field(
        ...,
        description="Настройки задержек для всплывающих окон",
    )
    update: UpdateConfig | None = Field(
        default=None,
        description="Информация об обновлении (если есть)",
    )


# Алиасы для обратной совместимости (deprecated)
InitResponseNative = InitResponse
InitResponseCasino = InitResponse
