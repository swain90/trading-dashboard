"""GET /api/trades — trade history with stats."""

from __future__ import annotations

from fastapi import APIRouter, Query

import database as db
from models import Trade, TradeStats, TradesResponse

router = APIRouter(prefix="/api")


@router.get("/trades", response_model=TradesResponse)
async def get_trades(
    days: int = Query(7, ge=1, le=90),
    bot: str | None = Query(None, description="Filter by bot_id"),
) -> TradesResponse:
    trades: list[Trade] = []

    bot_ids = [bot] if bot and bot in db.settings.bots else list(db.settings.bots)

    for bot_id in bot_ids:
        cfg = db.bot_config(bot_id)
        col = db.symbol_col(bot_id)

        rows = await db.fetch_all(
            bot_id,
            f"SELECT id, {col} AS symbol, side, quantity, entry_price, "
            f"exit_price, pnl, opened_at, closed_at "
            f"FROM trades "
            f"WHERE closed_at >= datetime('now', '-' || ? || ' days') "
            f"AND closed_at IS NOT NULL "
            f"ORDER BY closed_at DESC",
            (str(days),),
        )

        for r in rows:
            trades.append(
                Trade(
                    id=r["id"],
                    bot_id=bot_id,
                    bot_name=cfg.name,
                    symbol=r["symbol"],
                    side=r["side"],
                    quantity=r.get("quantity"),
                    entry_price=r.get("entry_price"),
                    exit_price=r.get("exit_price"),
                    pnl=r.get("pnl"),
                    opened_at=r.get("opened_at"),
                    closed_at=r.get("closed_at"),
                )
            )

    trades.sort(key=lambda t: t.closed_at or "", reverse=True)

    # Compute stats
    pnls = [t.pnl for t in trades if t.pnl is not None]
    wins = [p for p in pnls if p > 0]
    losses = [p for p in pnls if p <= 0]
    total_trades = len(pnls)

    stats = TradeStats(
        total_trades=total_trades,
        wins=len(wins),
        losses=len(losses),
        win_rate=round(len(wins) / total_trades * 100, 1) if total_trades else 0.0,
        total_pnl=round(sum(pnls), 2) if pnls else 0.0,
        best_trade=round(max(pnls), 2) if pnls else 0.0,
        worst_trade=round(min(pnls), 2) if pnls else 0.0,
        avg_pnl=round(sum(pnls) / total_trades, 2) if total_trades else 0.0,
    )

    return TradesResponse(trades=trades, stats=stats, count=len(trades))
