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
        col = db.symbol_col(bot_id)

        rows = await db.fetch_all(
            bot_id,
            f"SELECT id, {col} AS symbol, side, size, entry_price, "
            f"current_price, unrealized_pnl, stop_loss, take_profit, opened_at "
            f"FROM positions ORDER BY opened_at DESC",
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

    positions.sort(key=lambda p: p.opened_at or "", reverse=True)

    return PositionsResponse(positions=positions, count=len(positions))
