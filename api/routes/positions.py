"""GET /api/positions — open positions across all bots."""

from __future__ import annotations

from fastapi import APIRouter, Query

import database as db
from models import Position, PositionsResponse

router = APIRouter(prefix="/api")


@router.get("/positions", response_model=PositionsResponse)
async def get_positions(
    bot: str | None = Query(None, description="Filter by bot_id"),
) -> PositionsResponse:
    positions: list[Position] = []

    bot_ids = [bot] if bot and bot in db.settings.bots else list(db.settings.bots)

    for bot_id in bot_ids:
        cfg = db.bot_config(bot_id)
        table = cfg.table("positions")
        sym = db.col(bot_id, table, "symbol")
        sz = db.col(bot_id, table, "size")
        ep = db.col(bot_id, table, "entry_price")

        cp = db.col(bot_id, table, "current_price")
        urpnl = db.col(bot_id, table, "unrealized_pnl")
        sl = db.col(bot_id, table, "stop_loss")
        tp = db.col(bot_id, table, "take_profit")
        opened = db.col(bot_id, table, "opened_at")

        rows = await db.fetch_all(
            bot_id,
            f"SELECT id, {sym}, side, {sz}, {ep}, "
            f"{cp}, {urpnl}, {sl}, {tp}, {opened} "
            f"FROM {table} ORDER BY "
            f"{db.raw_col(bot_id, table, 'opened_at') or 'id'} DESC",
        )

        for r in rows:
            positions.append(
                Position(
                    id=r["id"],
                    bot_id=bot_id,
                    bot_name=cfg.name,
                    symbol=r["symbol"],
                    side=r["side"],
                    size=r["size"],
                    entry_price=r["entry_price"],
                    current_price=r.get("current_price"),
                    unrealized_pnl=r.get("unrealized_pnl"),
                    stop_loss=r.get("stop_loss"),
                    take_profit=r.get("take_profit"),
                    opened_at=r.get("opened_at"),
                )
            )

    positions.sort(
        key=lambda p: p.opened_at.isoformat() if p.opened_at else "",
        reverse=True,
    )

    return PositionsResponse(positions=positions, count=len(positions))
