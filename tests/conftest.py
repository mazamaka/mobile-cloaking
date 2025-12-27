"""Pytest fixtures for API tests."""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def client():
    """Async HTTP client for testing."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# Test data fixtures
@pytest.fixture
def valid_init_request() -> dict:
    """Valid /client/init request body."""
    return {
        "schema": 1,
        "app": {"bundle_id": "com.test.app", "version": "1.0.0"},
        "device": {"language": "en", "timezone": "Europe/Budapest", "region": "HU"},
        "privacy": {"att": "notDetermined"},
        "ids": {"internal_id": "550e8400-e29b-41d4-a716-446655440000"},
    }


@pytest.fixture
def valid_init_request_full() -> dict:
    """Valid /client/init request with all optional fields."""
    return {
        "schema": 1,
        "app": {"bundle_id": "com.test.full", "version": "2.0.0"},
        "device": {"language": "ru-RU", "timezone": "Europe/Moscow", "region": "RU"},
        "privacy": {"att": "authorized"},
        "ids": {
            "internal_id": "660e8400-e29b-41d4-a716-446655440001",
            "idfa": "AEBE52E7-03EE-455A-B3C4-E57283966239",
        },
        "attribution": {"appsflyer_id": "1765992827433-2791097"},
        "push": {"token": "abc123def456"},
    }


@pytest.fixture
def valid_event_request() -> dict:
    """Valid /client/event request body."""
    return {
        "schema": 1,
        "app": {"bundle_id": "com.test.app", "version": "1.0.0"},
        "ids": {"internal_id": "550e8400-e29b-41d4-a716-446655440000"},
        "event": {"name": "rate_sheet_shown", "ts": 1734541234, "props": None},
    }


@pytest.fixture
def valid_event_request_with_props() -> dict:
    """Valid /client/event request with event properties."""
    return {
        "schema": 1,
        "app": {"bundle_id": "com.test.app", "version": "1.0.0"},
        "ids": {"internal_id": "550e8400-e29b-41d4-a716-446655440000"},
        "event": {
            "name": "rate_slider_completed",
            "ts": 1734541300,
            "props": {"rating": 5, "source": "popup"},
        },
    }
