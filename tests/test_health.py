"""Tests for health check endpoints."""

import pytest


@pytest.mark.anyio
async def test_health_endpoint(client):
    """Test /health endpoint returns ok."""
    response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.anyio
async def test_ready_endpoint(client):
    """Test /ready endpoint returns ready."""
    response = await client.get("/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ready"}
