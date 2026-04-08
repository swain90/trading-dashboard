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


SCHEMA_FM_QUOTES = """
CREATE TABLE quotes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    con_id TEXT,
    symbol TEXT NOT NULL,
    strike REAL,
    expiry TEXT,
    side TEXT,
    price REAL,
    quantity INTEGER,
    order_id TEXT,
    status TEXT,
    created_at DATETIME,
    updated_at DATETIME
);
"""

SCHEMA_FM_FILLS = """
CREATE TABLE fills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    execution_id TEXT,
    con_id TEXT,
    symbol TEXT NOT NULL,
    strike REAL,
    expiry TEXT,
    side TEXT,
    price REAL,
    quantity INTEGER,
    execution_type TEXT,
    filled_at DATETIME
);
"""

SCHEMA_FM_INVENTORY = """
CREATE TABLE inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,
    strike REAL,
    expiry TEXT,
    side TEXT,
    quantity INTEGER,
    avg_cost REAL,
    current_value REAL,
    updated_at DATETIME
);
"""

SCHEMA_FM_DAILY_PNL = """
CREATE TABLE daily_pnl (
    date TEXT PRIMARY KEY,
    spread_pnl REAL,
    inventory_pnl REAL,
    coupon_income REAL,
    total_pnl REAL,
    num_pairs INTEGER,
    num_quotes INTEGER,
    fill_rate REAL
);
"""

SCHEMA_FM_BOT_STATE = """
CREATE TABLE bot_state (
    key TEXT PRIMARY KEY,
    value TEXT,
    updated_at DATETIME
);
"""


def _create_fm_db(path: str, seed: dict) -> None:
    conn = sqlite3.connect(path)
    conn.execute(SCHEMA_FM_QUOTES)
    conn.execute(SCHEMA_FM_FILLS)
    conn.execute(SCHEMA_FM_INVENTORY)
    conn.execute(SCHEMA_FM_DAILY_PNL)
    conn.execute(SCHEMA_FM_BOT_STATE)

    for q in seed.get("quotes", []):
        conn.execute(
            "INSERT INTO quotes (symbol, strike, expiry, side, price, quantity, status, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            q,
        )
    for f in seed.get("fills", []):
        conn.execute(
            "INSERT INTO fills (symbol, strike, expiry, side, price, quantity, filled_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            f,
        )
    for inv in seed.get("inventory", []):
        conn.execute(
            "INSERT INTO inventory (symbol, strike, expiry, side, quantity, avg_cost, current_value, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            inv,
        )
    for pnl in seed.get("daily_pnl", []):
        conn.execute(
            "INSERT INTO daily_pnl (date, spread_pnl, inventory_pnl, coupon_income, total_pnl, num_pairs, num_quotes, fill_rate) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            pnl,
        )
    for state in seed.get("bot_state", []):
        conn.execute(
            "INSERT INTO bot_state (key, value, updated_at) VALUES (?, ?, ?)",
            state,
        )

    conn.commit()
    conn.close()


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

    # Forecast Maker — prediction markets, different schema entirely
    fm_path = str(tmp_path / "forecast_maker.db")
    today_str = NOW.strftime("%Y-%m-%d")
    yesterday_str = (NOW - timedelta(days=1)).strftime("%Y-%m-%d")

    _create_fm_db(
        fm_path,
        {
            "quotes": [
                ("TRUMP.WIN", 0.55, "2026-11-03", "BUY", 0.52, 100, "filled", TODAY),
                ("FED.HIKE", 0.30, "2026-06-15", "SELL", 0.32, 50, "open", TODAY),
                ("GDP.3PCT", 0.45, "2026-09-30", "BUY", 0.44, 200, "filled", YESTERDAY),
            ],
            "fills": [
                ("TRUMP.WIN", 0.55, "2026-11-03", "BUY", 0.52, 100, TODAY),
                ("GDP.3PCT", 0.45, "2026-09-30", "BUY", 0.44, 200, YESTERDAY),
            ],
            "inventory": [
                ("TRUMP.WIN", 0.55, "2026-11-03", "LONG", 100, 0.52, 55.0, TODAY),
            ],
            "daily_pnl": [
                (today_str, 12.50, 3.00, 1.50, 17.00, 5, 20, 0.35),
                (yesterday_str, 8.00, -2.00, 1.50, 7.50, 4, 15, 0.30),
            ],
            "bot_state": [
                ("status", "running", TODAY),
            ],
        },
    )

    # Currency Compass — uses "symbol" and "signal_type", same schema as CH
    cc_path = str(tmp_path / "currency_compass.db")
    _create_db(
        cc_path,
        "symbol",
        {
            "signals": [
                ("EUR/USD", "LONG", 0.82, "macro_model", TODAY),
            ],
            "trades": [
                ("EUR/USD", "BUY", 10000, 1.0850, 1.0875, 25.00, YESTERDAY, TODAY),
            ],
            "positions": [
                ("GBP/USD", "LONG", 5000, 1.2650, 1.2680, 15.00, 1.2600, 1.2750, TODAY),
            ],
        },
        signals_ddl=SCHEMA_SIGNALS_CH,
    )

    return {"ww": ww_path, "ch": ch_path, "crypto": crypto_path, "fm": fm_path, "cc": cc_path}


@pytest.fixture()
def _configure_env(tmp_dbs):
    """Set environment variables pointing to temp DBs."""
    os.environ["WW_DB_PATH"] = tmp_dbs["ww"]
    os.environ["CH_DB_PATH"] = tmp_dbs["ch"]
    os.environ["CRYPTO_DB_PATH"] = tmp_dbs["crypto"]
    os.environ["FM_DB_PATH"] = tmp_dbs["fm"]
    os.environ["CC_DB_PATH"] = tmp_dbs["cc"]
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
    os.environ.pop("FM_DB_PATH", None)
    os.environ.pop("CC_DB_PATH", None)
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
