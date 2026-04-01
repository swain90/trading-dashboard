"""GET /api/health — bot status (no auth required)."""

from __future__ import annotations

from fastapi import APIRouter

import database as db
from models import BotHealth, HealthResponse

router = APIRouter(prefix="/api")


@router.get("/health", response_model=HealthResponse)
async def get_health() -> HealthResponse:
    bots: list[BotHealth] = []

    for bot_id in db.settings.bots:
        cfg = db.bot_config(bot_id)
        connected = db.get_connection(bot_id) is not None
        sig_table = cfg.table("signals")
        pos_table = cfg.table("positions")
        trade_table = cfg.table("trades")

        last_signal = None
        open_positions = 0
        trades_today = 0

        if connected:
            row = await db.fetch_one(
                bot_id,
                f"SELECT created_at FROM {sig_table} ORDER BY created_at DESC LIMIT 1",
            )
            last_signal = row["created_at"] if row else None

            row = await db.fetch_one(
                bot_id, f"SELECT COUNT(*) as cnt FROM {pos_table}",
            )
            open_positions = row["cnt"] if row else 0

            ts_col = db.raw_col(bot_id, trade_table, "closed_at") or "closed_at"
            row = await db.fetch_one(
                bot_id,
                f"SELECT COUNT(*) as cnt FROM {trade_table} "
                f"WHERE date({ts_col}) = date('now')",
            )
            trades_today = row["cnt"] if row else 0

        if db.has_table(bot_id, "bot_state"):
            status = await db.bot_state_status(bot_id)
        else:
            status = db.bot_status(bot_id, last_signal)

        bots.append(
            BotHealth(
                id=bot_id,
                name=cfg.name,
                status=status,
                db_connected=connected,
                last_signal=last_signal,
                open_positions=open_positions,
                trades_today=trades_today,
            )
        )

    overall = "ok" if any(b.db_connected for b in bots) else "degraded"

    return HealthResponse(status=overall, bots=bots)
