"""Tests for GET /api/overview."""

import pytest


@pytest.mark.asyncio
async def test_overview_returns_all_bots(client):
    resp = await client.get("/api/overview")
    assert resp.status_code == 200
    data = resp.json()
    assert "combined" in data
    assert "bots" in data
    assert len(data["bots"]) == 4


@pytest.mark.asyncio
async def test_overview_combined_totals(client):
    resp = await client.get("/api/overview")
    data = resp.json()
    combined = data["combined"]
    bots = data["bots"]

    # Combined should sum up bot values
    assert combined["open_positions"] == sum(b["open_positions"] for b in bots)
    assert combined["signals_today"] == sum(b["signals_today"] for b in bots)


@pytest.mark.asyncio
async def test_overview_bot_fields(client):
    resp = await client.get("/api/overview")
    bot = resp.json()["bots"][0]

    required_fields = [
        "id", "name", "asset_class", "equity", "today_pnl",
        "today_pnl_pct", "open_positions", "signals_today", "status",
    ]
    for field in required_fields:
        assert field in bot, f"Missing field: {field}"


@pytest.mark.asyncio
async def test_overview_forecast_maker_daily_pnl(client):
    """Forecast Maker gets P&L from daily_pnl table, not trades."""
    resp = await client.get("/api/overview")
    bots = {b["id"]: b for b in resp.json()["bots"]}
    fm = bots["forecast_maker"]
    assert fm["asset_class"] == "predictions"
    # Equity = sum of all daily_pnl total_pnl: 17.00 + 7.50 = 24.50
    assert fm["equity"] == 24.50
    # Today's P&L from daily_pnl
    assert fm["today_pnl"] == 17.00
    assert fm["open_positions"] == 1  # 1 inventory row
    assert fm["status"] == "running"  # from bot_state


@pytest.mark.asyncio
async def test_overview_whale_watcher_uses_ticker_normalized(client):
    """Whale Watcher uses 'ticker' internally but API returns data correctly."""
    resp = await client.get("/api/overview")
    bots = {b["id"]: b for b in resp.json()["bots"]}
    ww = bots["whale_watcher"]
    # WW has 1 signal today, 1 position
    assert ww["signals_today"] >= 1
    assert ww["open_positions"] == 1
