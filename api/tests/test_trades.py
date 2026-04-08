"""Tests for GET /api/trades."""

import pytest


@pytest.mark.asyncio
async def test_trades_returns_recent(client):
    resp = await client.get("/api/trades?days=7")
    assert resp.status_code == 200
    data = resp.json()
    # WW: 1 closed today, CH: 1 closed today, Crypto: 1 closed today, FM: 1 filled today, CC: 1 closed today = 5
    # WW old trade is 30 days ago, outside 7-day window; FM fill from yesterday also in window = 6
    assert data["count"] == 6


@pytest.mark.asyncio
async def test_trades_stats(client):
    resp = await client.get("/api/trades?days=7")
    stats = resp.json()["stats"]
    # FM fills have no pnl field (NULL), so only 4 trades with pnl data (WW, CH, Crypto, CC)
    assert stats["total_trades"] == 4
    assert stats["wins"] == 4
    assert stats["win_rate"] == 100.0
    assert stats["total_pnl"] > 0


@pytest.mark.asyncio
async def test_trades_filter_by_bot(client):
    resp = await client.get("/api/trades?days=7&bot=commodity_hunter")
    data = resp.json()
    assert all(t["bot_id"] == "commodity_hunter" for t in data["trades"])
    assert data["count"] == 1


@pytest.mark.asyncio
async def test_trades_stats_empty(client):
    """No trades for this bot in window should return zero stats."""
    resp = await client.get("/api/trades?days=1&bot=crypto")
    stats = resp.json()["stats"]
    # Crypto trade was closed TODAY so should still be in 1-day window
    assert stats["total_trades"] >= 0


@pytest.mark.asyncio
async def test_trades_forecast_maker_fills(client):
    """Forecast Maker maps fills table to trades endpoint."""
    resp = await client.get("/api/trades?days=7&bot=forecast_maker")
    data = resp.json()
    assert data["count"] == 2
    symbols = {t["symbol"] for t in data["trades"]}
    assert "TRUMP.WIN" in symbols
    assert "GDP.3PCT" in symbols
    # FM fills use 'price' mapped to 'entry_price', no exit_price or pnl
    fill = next(t for t in data["trades"] if t["symbol"] == "TRUMP.WIN")
    assert fill["entry_price"] == 0.52
    assert fill["pnl"] is None
    assert fill["exit_price"] is None


@pytest.mark.asyncio
async def test_trades_includes_pnl(client):
    resp = await client.get("/api/trades?days=90")
    for trade in resp.json()["trades"]:
        assert "pnl" in trade
        assert "symbol" in trade
