"""Read-only async SQLite connections to all 3 bot databases."""

from __future__ import annotations

import logging
from datetime import datetime, timezone

import aiosqlite

from config import BotConfig, settings

logger = logging.getLogger(__name__)

# Active connections keyed by bot_id
_connections: dict[str, aiosqlite.Connection] = {}

# Schema cache: _schemas[bot_id][table_name] = set of column names
_schemas: dict[str, dict[str, set[str]]] = {}

# Column aliases: maps (normalized_name) -> list of possible actual column names
# First match wins when introspecting a table
COLUMN_ALIASES: dict[str, list[str]] = {
    "symbol": ["symbol", "ticker"],
    "direction": ["direction", "signal_type", "side"],
    "size": ["size", "quantity"],
    "entry_price": ["entry_price", "avg_cost", "price"],
    "closed_at": ["closed_at", "filled_at"],
}


async def _introspect(bot_id: str, conn: aiosqlite.Connection) -> None:
    """Read PRAGMA table_info() for all tables and cache column names."""
    tables_schema: dict[str, set[str]] = {}
    try:
        async with conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ) as cur:
            tables = [row[0] for row in await cur.fetchall()]

        for table in tables:
            async with conn.execute(f"PRAGMA table_info({table})") as cur:
                cols = {row[1] for row in await cur.fetchall()}
            tables_schema[table] = cols

        _schemas[bot_id] = tables_schema
        logger.info(
            "Introspected %s: %s",
            bot_id,
            {t: sorted(c) for t, c in tables_schema.items()},
        )
    except Exception:
        logger.exception("Schema introspection failed for %s", bot_id)
        _schemas[bot_id] = {}


async def open_all() -> None:
    """Open read-only connections to all configured bot databases."""
    for bot_id, bot in settings.bots.items():
        try:
            uri = f"file:{bot.db_path}?mode=ro"
            conn = await aiosqlite.connect(uri, uri=True)
            conn.row_factory = aiosqlite.Row
            _connections[bot_id] = conn
            await _introspect(bot_id, conn)
            logger.info("Connected to %s (%s)", bot.name, bot.db_path)
        except Exception:
            logger.warning("Could not connect to %s (%s)", bot.name, bot.db_path)


async def close_all() -> None:
    """Close all open database connections."""
    for bot_id, conn in _connections.items():
        try:
            await conn.close()
        except Exception:
            logger.warning("Error closing connection for %s", bot_id)
    _connections.clear()
    _schemas.clear()


def get_connection(bot_id: str) -> aiosqlite.Connection | None:
    """Get the connection for a specific bot, or None if unavailable."""
    return _connections.get(bot_id)


def available_bots() -> list[str]:
    """Return bot_ids that have active DB connections."""
    return list(_connections.keys())


def bot_config(bot_id: str) -> BotConfig:
    """Get the config for a bot."""
    return settings.bots[bot_id]


def symbol_col(bot_id: str) -> str:
    """Return the ticker/symbol column name for a bot's SQL queries."""
    return settings.bots[bot_id].ticker_field


def table_name(bot_id: str, logical: str) -> str:
    """Resolve a logical table name to the actual table name for a bot."""
    return settings.bots[bot_id].table(logical)


def col(bot_id: str, table: str, normalized_name: str) -> str:
    """Return a SQL fragment that selects the actual column aliased to normalized_name.

    Uses PRAGMA-introspected schema to find which actual column exists.
    Falls back to NULL if no matching column is found.

    Examples:
        col("whale_watcher", "signals", "symbol")  -> "ticker AS symbol"
        col("commodity_hunter", "signals", "direction")  -> "signal_type AS direction"
        col("crypto", "signals", "direction")  -> "direction"
    """
    actual_cols = _schemas.get(bot_id, {}).get(table, set())

    # Check alias list first
    candidates = COLUMN_ALIASES.get(normalized_name, [normalized_name])
    for candidate in candidates:
        if candidate in actual_cols:
            if candidate == normalized_name:
                return normalized_name
            return f"{candidate} AS {normalized_name}"

    # Column doesn't exist in this table — return NULL
    return f"NULL AS {normalized_name}"


def raw_col(bot_id: str, table: str, normalized_name: str) -> str | None:
    """Return the actual column name for a normalized name, or None if missing."""
    actual_cols = _schemas.get(bot_id, {}).get(table, set())
    candidates = COLUMN_ALIASES.get(normalized_name, [normalized_name])
    for candidate in candidates:
        if candidate in actual_cols:
            return candidate
    return None


def has_col(bot_id: str, table: str, normalized_name: str) -> bool:
    """Check if a table has a column (or any alias for it)."""
    actual_cols = _schemas.get(bot_id, {}).get(table, set())
    candidates = COLUMN_ALIASES.get(normalized_name, [normalized_name])
    return any(c in actual_cols for c in candidates)


async def fetch_all(bot_id: str, sql: str, params: tuple = ()) -> list[dict]:
    """Run a query and return all rows as dicts. Returns [] if bot unavailable."""
    conn = get_connection(bot_id)
    if conn is None:
        return []
    try:
        async with conn.execute(sql, params) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    except Exception:
        logger.exception("Query failed for %s: %s", bot_id, sql)
        return []


async def fetch_one(bot_id: str, sql: str, params: tuple = ()) -> dict | None:
    """Run a query and return one row as dict. Returns None if unavailable."""
    conn = get_connection(bot_id)
    if conn is None:
        return None
    try:
        async with conn.execute(sql, params) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None
    except Exception:
        logger.exception("Query failed for %s: %s", bot_id, sql)
        return None


def has_table(bot_id: str, table: str) -> bool:
    """Check if a bot's database has a specific table."""
    return table in _schemas.get(bot_id, {})


def bot_status(bot_id: str, last_signal_time: str | None) -> str:
    """Determine bot status based on DB connection and last signal time."""
    if get_connection(bot_id) is None:
        return "unavailable"
    if last_signal_time is None:
        return "stopped"
    try:
        last = datetime.fromisoformat(last_signal_time).replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        if (now - last).total_seconds() < 86400:
            return "running"
    except (ValueError, TypeError):
        pass
    return "stopped"


async def bot_state_status(bot_id: str) -> str:
    """Get bot status from bot_state table (Forecast Maker). Falls back to 'stopped'."""
    if get_connection(bot_id) is None:
        return "unavailable"
    if not has_table(bot_id, "bot_state"):
        return "stopped"
    row = await fetch_one(
        bot_id,
        "SELECT value FROM bot_state WHERE key = 'status'",
    )
    if row and row["value"]:
        return row["value"].lower()
    return "stopped"
