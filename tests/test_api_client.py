"""Tests for /api/v1/client endpoints."""

import uuid

import pytest


class TestClientInit:
    """Tests for POST /api/v1/client/init endpoint."""

    @pytest.mark.anyio
    async def test_init_returns_200_for_new_app(self, client, valid_init_request):
        """New app defaults to NATIVE mode, returns 200."""
        # Use unique bundle_id to ensure new app
        valid_init_request["app"]["bundle_id"] = f"com.test.{uuid.uuid4().hex[:8]}"

        response = await client.post(
            "/api/v1/client/init",
            json=valid_init_request,
            headers={"X-Schema": "1"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "prompts" in data
        assert "rate_delay_sec" in data["prompts"]
        assert "push_delay_sec" in data["prompts"]

    @pytest.mark.anyio
    async def test_init_with_full_request(self, client, valid_init_request_full):
        """Init with all optional fields works correctly."""
        valid_init_request_full["app"]["bundle_id"] = f"com.test.full.{uuid.uuid4().hex[:8]}"

        response = await client.post(
            "/api/v1/client/init",
            json=valid_init_request_full,
            headers={"X-Schema": "1"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "prompts" in data

    @pytest.mark.anyio
    async def test_init_increments_session_count(self, client, valid_init_request):
        """Multiple inits from same client increment sessions_count."""
        unique_internal_id = str(uuid.uuid4())
        valid_init_request["ids"]["internal_id"] = unique_internal_id
        valid_init_request["app"]["bundle_id"] = f"com.test.sessions.{uuid.uuid4().hex[:8]}"

        # First init
        response1 = await client.post(
            "/api/v1/client/init",
            json=valid_init_request,
            headers={"X-Schema": "1"},
        )
        assert response1.status_code == 200

        # Second init (same internal_id)
        response2 = await client.post(
            "/api/v1/client/init",
            json=valid_init_request,
            headers={"X-Schema": "1"},
        )
        assert response2.status_code == 200

    @pytest.mark.anyio
    async def test_init_missing_required_fields(self, client):
        """Init with missing required fields returns 422."""
        incomplete_request = {
            "schema": 1,
            "app": {"bundle_id": "com.test.app"},
            # missing version, device, privacy, ids
        }

        response = await client.post(
            "/api/v1/client/init",
            json=incomplete_request,
            headers={"X-Schema": "1"},
        )

        assert response.status_code == 422

    @pytest.mark.anyio
    async def test_init_invalid_att_status(self, client, valid_init_request):
        """Init with invalid ATT status returns 422."""
        valid_init_request["privacy"]["att"] = "invalid_status"

        response = await client.post(
            "/api/v1/client/init",
            json=valid_init_request,
            headers={"X-Schema": "1"},
        )

        assert response.status_code == 422

    @pytest.mark.anyio
    async def test_init_all_att_statuses(self, client, valid_init_request):
        """Init works with all valid ATT statuses."""
        att_statuses = ["authorized", "denied", "notDetermined", "restricted", "legacy", "unavailable"]

        for att_status in att_statuses:
            valid_init_request["ids"]["internal_id"] = str(uuid.uuid4())
            valid_init_request["app"]["bundle_id"] = f"com.test.att.{uuid.uuid4().hex[:8]}"
            valid_init_request["privacy"]["att"] = att_status

            response = await client.post(
                "/api/v1/client/init",
                json=valid_init_request,
                headers={"X-Schema": "1"},
            )

            assert response.status_code == 200, f"Failed for ATT status: {att_status}"


class TestClientEvent:
    """Tests for POST /api/v1/client/event endpoint."""

    @pytest.mark.anyio
    async def test_event_returns_empty_object(self, client, valid_init_request, valid_event_request):
        """Event endpoint returns empty JSON object."""
        # First create client via init
        valid_init_request["ids"]["internal_id"] = valid_event_request["ids"]["internal_id"]
        await client.post(
            "/api/v1/client/init",
            json=valid_init_request,
            headers={"X-Schema": "1"},
        )

        # Then send event
        response = await client.post(
            "/api/v1/client/event",
            json=valid_event_request,
            headers={"X-Schema": "1"},
        )

        assert response.status_code == 200
        assert response.json() == {}

    @pytest.mark.anyio
    async def test_event_with_props(self, client, valid_init_request, valid_event_request_with_props):
        """Event with properties is recorded correctly."""
        # First create client via init
        valid_init_request["ids"]["internal_id"] = valid_event_request_with_props["ids"]["internal_id"]
        await client.post(
            "/api/v1/client/init",
            json=valid_init_request,
            headers={"X-Schema": "1"},
        )

        response = await client.post(
            "/api/v1/client/event",
            json=valid_event_request_with_props,
            headers={"X-Schema": "1"},
        )

        assert response.status_code == 200
        assert response.json() == {}

    @pytest.mark.anyio
    async def test_event_unknown_client(self, client):
        """Event for unknown client still succeeds (creates orphan event)."""
        event_request = {
            "schema": 1,
            "app": {"bundle_id": "com.test.unknown", "version": "1.0.0"},
            "ids": {"internal_id": str(uuid.uuid4())},
            "event": {"name": "test_event", "ts": 1734541234, "props": None},
        }

        response = await client.post(
            "/api/v1/client/event",
            json=event_request,
            headers={"X-Schema": "1"},
        )

        # Should still return 200 (event logged even without client)
        assert response.status_code == 200

    @pytest.mark.anyio
    async def test_event_missing_required_fields(self, client):
        """Event with missing required fields returns 422."""
        incomplete_request = {
            "schema": 1,
            "app": {"bundle_id": "com.test.app"},
            # missing version, ids, event
        }

        response = await client.post(
            "/api/v1/client/event",
            json=incomplete_request,
            headers={"X-Schema": "1"},
        )

        assert response.status_code == 422

    @pytest.mark.anyio
    async def test_event_various_names(self, client, valid_init_request, valid_event_request):
        """Various event names are accepted."""
        event_names = [
            "rate_sheet_shown",
            "rate_slider_completed",
            "rate_sheet_closed",
            "push_prompt_shown",
            "push_prompt_accepted",
            "push_prompt_declined",
            "custom_event",
        ]

        # Create client first
        valid_init_request["ids"]["internal_id"] = valid_event_request["ids"]["internal_id"]
        await client.post(
            "/api/v1/client/init",
            json=valid_init_request,
            headers={"X-Schema": "1"},
        )

        for event_name in event_names:
            valid_event_request["event"]["name"] = event_name
            valid_event_request["event"]["ts"] += 1  # increment timestamp

            response = await client.post(
                "/api/v1/client/event",
                json=valid_event_request,
                headers={"X-Schema": "1"},
            )

            assert response.status_code == 200, f"Failed for event: {event_name}"
