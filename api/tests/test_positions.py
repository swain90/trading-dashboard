"""Tests for GET /api/positions."""

import pytest


@pytest.mark.asyncio
async def test_positions_returns_all(client):
    resp = await client.get("/api/positions")
    assert resp.status_code == 200
    data = resp.json()
    # WW has 1 position, CH has 1, Crypto has 0 = 2 total
    assert data["count"] == 2
    assert len(data["positions"]) == 2


@pytest.mark.asyncio
async def test_positions_tagged_with_bot(client):
    resp = await client.get("/api/positions")
    for pos in resp.json()["positions"]:
        assert "bot_id" in pos
        assert "bot_name" in pos
        assert pos["bot_id"] in ["whale_watcher", "commodity_hunter", "crypto"]


@pytest.mark.asyncio
async def test_positions_filter_by_bot(client):
    resp = await client.get("/api/positions?bot=whale_watcher")
    data = resp.json()
    assert data["count"] == 1
    assert data["positions"][0]["bot_id"] == "whale_watcher"
    assert data["positions"][0]["symbol"] == "NVDA"


@pytest.mark.asyncio
async def test_positions_symbol_normalized(client):
    """All positions use 'symbol' field regardless of bot's internal column name."""
    resp = await client.get("/api/positions")
    for pos in resp.json()["positions"]:
        assert "symbol" in pos
        assert pos["symbol"] is not None
