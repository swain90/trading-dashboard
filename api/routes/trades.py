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
        table = cfg.table("trades")
        sym = db.col(bot_id, table, "symbol")
        ep = db.col(bot_id, table, "entry_price")
        ca = db.col(bot_id, table, "closed_at")
        # Actual column name for WHERE clause (no alias)
        ts_col = db.raw_col(bot_id, table, "closed_at") or "closed_at"

        exit_p = db.col(bot_id, table, "exit_price")
        pnl_col = db.col(bot_id, table, "pnl")
        opened = db.col(bot_id, table, "opened_at")

        rows = await db.fetch_all(
            bot_id,
            f"SELECT id, {sym}, side, quantity, {ep}, "
            f"{exit_p}, {pnl_col}, {opened}, {ca} "
            f"FROM {table} "
            f"WHERE {ts_col} >= datetime('now', '-' || ? || ' days') "
            f"AND {ts_col} IS NOT NULL "
            f"ORDER BY {ts_col} DESC",
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
