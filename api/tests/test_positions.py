"""Tests for GET /api/positions."""

import pytest


@pytest.mark.asyncio
async def test_positions_returns_all(client):
    resp = await client.get("/api/positions")
    assert resp.status_code == 200
    data = resp.json()
    # WW has 1 position, CH has 1, Crypto has 0, FM has 1 = 3 total
    assert data["count"] == 3
    assert len(data["positions"]) == 3


@pytest.mark.asyncio
async def test_positions_tagged_with_bot(client):
    resp = await client.get("/api/positions")
    for pos in resp.json()["positions"]:
        assert "bot_id" in pos
        assert "bot_name" in pos
        assert pos["bot_id"] in ["whale_watcher", "commodity_hunter", "crypto", "forecast_maker"]


@pytest.mark.asyncio
async def test_positions_filter_by_bot(client):
    resp = await client.get("/api/positions?bot=whale_watcher")
    data = resp.json()
    assert data["count"] == 1
    assert data["positions"][0]["bot_id"] == "whale_watcher"
    assert data["positions"][0]["symbol"] == "NVDA"


@pytest.mark.asyncio
async def test_positions_forecast_maker_inventory(client):
    """Forecast Maker maps inventory table to positions endpoint."""
    resp = await client.get("/api/positions?bot=forecast_maker")
    data = resp.json()
    assert data["count"] == 1
    pos = data["positions"][0]
    assert pos["symbol"] == "TRUMP.WIN"
    assert pos["size"] == 100  # mapped from 'quantity'
    assert pos["entry_price"] == 0.52  # mapped from 'avg_cost'
    assert pos["bot_name"] == "Forecast Maker"


@pytest.mark.asyncio
async def test_positions_symbol_normalized(client):
    """All positions use 'symbol' field regardless of bot's internal column name."""
    resp = await client.get("/api/positions")
    for pos in resp.json()["positions"]:
        assert "symbol" in pos
        assert pos["symbol"] is not None
