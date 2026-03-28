"""Tests for GET /api/health."""

import pytest


@pytest.mark.asyncio
async def test_health_returns_all_bots(client):
    resp = await client.get("/api/health", headers={})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert len(data["bots"]) == 3


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
    for bot_id in ["whale_watcher", "commodity_hunter", "crypto"]:
        assert bots[bot_id]["db_connected"] is True
