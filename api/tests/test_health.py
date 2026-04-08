"""Tests for GET /api/health."""

import pytest

from config import settings


@pytest.mark.asyncio
async def test_health_returns_all_bots(client):
    resp = await client.get("/api/health", headers={})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert len(data["bots"]) == len(settings.bots)


@pytest.mark.asyncio
async def test_health_bot_fields(client):
    resp = await client.get("/api/health", headers={})
    bot = resp.json()["bots"][0]
    for field in ["id", "name", "status", "db_connected", "open_positions", "trades_today"]:
        assert field in bot


@pytest.mark.asyncio
async def test_health_db_connected(client):
    resp = await client.get("/api/health", headers={})
    bots = {b["id"]: b for b in resp.json()["bots"]}
    # All 3 test DBs should be connected
    for bot_id in settings.bots:
        assert bots[bot_id]["db_connected"] is True


@pytest.mark.asyncio
async def test_health_forecast_maker_status_from_bot_state(client):
    """Forecast Maker gets status from bot_state table."""
    resp = await client.get("/api/health", headers={})
    bots = {b["id"]: b for b in resp.json()["bots"]}
    fm = bots["forecast_maker"]
    assert fm["status"] == "running"
    assert fm["db_connected"] is True
