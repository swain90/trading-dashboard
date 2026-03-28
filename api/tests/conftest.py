"""Shared test fixtures: temp SQLite databases with seed data, test client."""

from __future__ import annotations

import os
import sqlite3
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

# Ensure api/ is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

NOW = datetime.now(timezone.utc)
TODAY = NOW.strftime("%Y-%m-%d %H:%M:%S")
YESTERDAY = (NOW - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
OLD = (NOW - timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")

SCHEMA_SIGNALS_WW = """
CREATE TABLE signals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT,
    ticker TEXT NOT NULL,
    signal_type TEXT,
    score REAL,
    raw_data TEXT,
    created_at DATETIME
);
"""

SCHEMA_SIGNALS_CH = """
CREATE TABLE signals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT,
    symbol TEXT NOT NULL,
    signal_type TEXT,
    score REAL,
    confidence REAL,
    raw_data TEXT,
    created_at DATETIME,
    expires_at DATETIME
);
"""

SCHEMA_SIGNALS_CRYPTO = """
CREATE TABLE signals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT,
    symbol TEXT NOT NULL,
    signal_type TEXT,
    score REAL,
    raw_data TEXT,
    created_at DATETIME
);
"""

SCHEMA_TRADES = """
CREATE TABLE trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    {ticker_col} TEXT NOT NULL,
    side TEXT,
    quantity REAL,
    entry_price REAL,
    exit_price REAL,
    pnl REAL,
    opened_at DATETIME,
    closed_at DATETIME,
    status TEXT DEFAULT 'closed'
);
"""

SCHEMA_POSITIONS = """
CREATE TABLE positions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    {ticker_col} TEXT NOT NULL,
    side TEXT,
    size REAL,
    entry_price REAL,
    current_price REAL,
    unrealized_pnl REAL,
    stop_loss REAL,
    take_profit REAL,
    opened_at DATETIME
);
"""


def _create_db(path: str, ticker_col: str, seed: dict, signals_ddl: str) -> None:
    conn = sqlite3.connect(path)
    conn.execute(signals_ddl)
    conn.execute(SCHEMA_TRADES.format(ticker_col=ticker_col))
    conn.execute(SCHEMA_POSITIONS.format(ticker_col=ticker_col))

    for sig in seed.get("signals", []):
        conn.execute(
            f"INSERT INTO signals ({ticker_col}, signal_type, score, source, created_at) "
            f"VALUES (?, ?, ?, ?, ?)",
            sig,
        )

    for trade in seed.get("trades", []):
        conn.execute(
            f"INSERT INTO trades ({ticker_col}, side, quantity, entry_price, exit_price, pnl, opened_at, closed_at) "
            f"VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            trade,
        )

    for pos in seed.get("positions", []):
        conn.execute(
            f"INSERT INTO positions ({ticker_col}, side, size, entry_price, current_price, unrealized_pnl, stop_loss, take_profit, opened_at) "
            f"VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            pos,
        )

    conn.commit()
    conn.close()


@pytest.fixture()
def tmp_dbs(tmp_path):
    """Create 3 temp SQLite databases with seed data."""
    ww_path = str(tmp_path / "trading.db")
    ch_path = str(tmp_path / "commodity.db")
    crypto_path = str(tmp_path / "crypto.db")

    # Whale Watcher — uses "ticker" and "signal_type"
    _create_db(
        ww_path,
        "ticker",
        {
            "signals": [
                ("AAPL", "LONG", 0.9, "whale_alert", TODAY),
                ("MSFT", "SHORT", 0.7, "flow_scan", YESTERDAY),
            ],
            "trades": [
                ("AAPL", "BUY", 100, 178.50, 181.20, 270.00, YESTERDAY, TODAY),
                ("TSLA", "BUY", 50, 200.00, 195.00, -250.00, OLD, OLD),
            ],
            "positions": [
                ("NVDA", "LONG", 50, 450.00, 460.00, 500.00, 440.00, 480.00, TODAY),
            ],
        },
        signals_ddl=SCHEMA_SIGNALS_WW,
    )

    # Commodity Hunter — uses "symbol" and "signal_type", has confidence + expires_at
    _create_db(
        ch_path,
        "symbol",
        {
            "signals": [
                ("MES", "LONG", 0.85, "momentum", TODAY),
            ],
            "trades": [
                ("MES", "BUY", 2, 5234.50, 5248.25, 137.50, YESTERDAY, TODAY),
            ],
            "positions": [
                ("MNQ", "SHORT", 1, 18500.00, 18450.00, 50.00, 18600.00, 18300.00, TODAY),
            ],
        },
        signals_ddl=SCHEMA_SIGNALS_CH,
    )

    # Crypto — uses "symbol" and "signal_type"
    _create_db(
        crypto_path,
        "symbol",
        {
            "signals": [
                ("BTC-USDT", "LONG", 0.87, "whale_flow", TODAY),
                ("ETH-USDT", "SHORT", 0.65, "momentum", TODAY),
            ],
            "trades": [
                ("BTC-USDT", "BUY", 0.1, 65000.00, 66500.00, 150.00, YESTERDAY, TODAY),
            ],
            "positions": [],
        },
        signals_ddl=SCHEMA_SIGNALS_CRYPTO,
    )

    return {"ww": ww_path, "ch": ch_path, "crypto": crypto_path}


@pytest.fixture()
def _configure_env(tmp_dbs):
    """Set environment variables pointing to temp DBs."""
    os.environ["WW_DB_PATH"] = tmp_dbs["ww"]
    os.environ["CH_DB_PATH"] = tmp_dbs["ch"]
    os.environ["CRYPTO_DB_PATH"] = tmp_dbs["crypto"]
    os.environ["DASHBOARD_API_KEY"] = "test-key-123"
    os.environ["CORS_ORIGINS"] = "http://localhost:5173"

    # Re-import config to pick up new env
    import config
    import importlib
    importlib.reload(config)

    # Update settings in database module
    import database
    database.settings = config.settings

    yield

    # Cleanup
    os.environ.pop("WW_DB_PATH", None)
    os.environ.pop("CH_DB_PATH", None)
    os.environ.pop("CRYPTO_DB_PATH", None)
    os.environ.pop("DASHBOARD_API_KEY", None)


@pytest.fixture()
async def client(_configure_env):
    """Async test client with DB connections open."""
    import importlib
    import database
    import main as main_mod
    importlib.reload(database)
    importlib.reload(main_mod)

    import config
    database.settings = config.settings

    await database.open_all()

    async with AsyncClient(
        transport=ASGITransport(app=main_mod.app),
        base_url="http://test",
        headers={"X-API-Key": "test-key-123"},
    ) as ac:
        yield ac

    await database.close_all()
