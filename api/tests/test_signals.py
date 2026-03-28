"""Tests for GET /api/signals."""

import pytest


@pytest.mark.asyncio
async def test_signals_returns_recent(client):
    resp = await client.get("/api/signals")
    assert resp.status_code == 200
    data = resp.json()
    # WW: 2 signals, CH: 1, Crypto: 2 = 5 total
    assert data["count"] == 5


@pytest.mark.asyncio
async def test_signals_limit(client):
    resp = await client.get("/api/signals?limit=2")
    data = resp.json()
    assert data["count"] <= 2


@pytest.mark.asyncio
async def test_signals_filter_by_bot(client):
    resp = await client.get("/api/signals?bot=crypto")
    data = resp.json()
    assert all(s["bot_id"] == "crypto" for s in data["signals"])
    assert data["count"] == 2


@pytest.mark.asyncio
async def test_signals_sorted_by_time_desc(client):
    resp = await client.get("/api/signals")
    signals = resp.json()["signals"]
    times = [s["created_at"] for s in signals if s["created_at"]]
    assert times == sorted(times, reverse=True)


@pytest.mark.asyncio
async def test_signals_fields(client):
    resp = await client.get("/api/signals")
    sig = resp.json()["signals"][0]
    for field in ["id", "bot_id", "bot_name", "symbol", "direction"]:
        assert field in sig
