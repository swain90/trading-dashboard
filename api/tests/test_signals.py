"""Tests for GET /api/signals."""

import pytest


@pytest.mark.asyncio
async def test_signals_returns_recent(client):
    resp = await client.get("/api/signals")
    assert resp.status_code == 200
    data = resp.json()
    # WW: 2 signals, CH: 1, Crypto: 2, FM: 3 quotes = 8 total
    assert data["count"] == 8


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


@pytest.mark.asyncio
async def test_signals_schema_mapping_ch_signal_type(client):
    """Commodity Hunter uses 'signal_type' not 'direction' — should be normalized."""
    resp = await client.get("/api/signals?bot=commodity_hunter")
    data = resp.json()
    assert data["count"] == 1
    sig = data["signals"][0]
    assert sig["direction"] == "LONG"
    assert sig["symbol"] == "MES"


@pytest.mark.asyncio
async def test_signals_schema_mapping_ww_ticker_and_signal_type(client):
    """Whale Watcher uses 'ticker' AND 'signal_type' — both normalized."""
    resp = await client.get("/api/signals?bot=whale_watcher")
    data = resp.json()
    assert data["count"] == 2
    symbols = {s["symbol"] for s in data["signals"]}
    assert "AAPL" in symbols
    assert "MSFT" in symbols
    # WW also uses signal_type, should be mapped to direction
    directions = {s["direction"] for s in data["signals"]}
    assert "LONG" in directions
    assert "SHORT" in directions


@pytest.mark.asyncio
async def test_signals_all_bots_have_direction(client):
    """All bots should map their direction-like field to 'direction' in API response."""
    resp = await client.get("/api/signals")
    for sig in resp.json()["signals"]:
        assert sig["direction"] in ("LONG", "SHORT", "BUY", "SELL"), (
            f"Bot {sig['bot_id']} signal {sig['id']} has direction={sig['direction']!r}"
        )


@pytest.mark.asyncio
async def test_signals_forecast_maker_quotes_as_signals(client):
    """Forecast Maker maps quotes table to signals endpoint."""
    resp = await client.get("/api/signals?bot=forecast_maker")
    data = resp.json()
    assert data["count"] == 3
    symbols = {s["symbol"] for s in data["signals"]}
    assert "TRUMP.WIN" in symbols
    assert "FED.HIKE" in symbols
    # FM uses 'side' mapped to 'direction'
    directions = {s["direction"] for s in data["signals"]}
    assert "BUY" in directions
    assert "SELL" in directions
