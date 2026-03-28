"""Read-only async SQLite connections to all 3 bot databases."""

from __future__ import annotations

import logging
from datetime import datetime, timezone

import aiosqlite

from config import BotConfig, settings

logger = logging.getLogger(__name__)

# Active connections keyed by bot_id
_connections: dict[str, aiosqlite.Connection] = {}


async def open_all() -> None:
    """Open read-only connections to all configured bot databases."""
    for bot_id, bot in settings.bots.items():
        try:
            uri = f"file:{bot.db_path}?mode=ro"
            conn = await aiosqlite.connect(uri, uri=True)
            conn.row_factory = aiosqlite.Row
            _connections[bot_id] = conn
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
