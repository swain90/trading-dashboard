"""GET /api/overview — combined equity and P&L per bot."""

from __future__ import annotations

from fastapi import APIRouter

import database as db
from models import BotOverview, CombinedOverview, OverviewResponse

router = APIRouter(prefix="/api")


@router.get("/overview", response_model=OverviewResponse)
async def get_overview() -> OverviewResponse:
    bots: list[BotOverview] = []

    for bot_id in db.settings.bots:
        cfg = db.bot_config(bot_id)
        sig_table = cfg.table("signals")
        pos_table = cfg.table("positions")

        if db.has_table(bot_id, "daily_pnl"):
            # Forecast Maker: P&L from daily_pnl table
            row = await db.fetch_one(
                bot_id,
                "SELECT COALESCE(total_pnl, 0) as today_pnl "
                "FROM daily_pnl WHERE date = date('now')",
            )
            today_pnl = row["today_pnl"] if row else 0.0

            row = await db.fetch_one(
                bot_id,
                "SELECT COALESCE(SUM(total_pnl), 0) as equity FROM daily_pnl",
            )
            equity = row["equity"] if row else 0.0
        else:
            # Standard bots: P&L from trades + positions
            row = await db.fetch_one(
                bot_id,
                "SELECT COALESCE(SUM(pnl), 0) as today_pnl "
                "FROM trades WHERE date(closed_at) = date('now') AND pnl IS NOT NULL",
            )
            closed_pnl = row["today_pnl"] if row else 0.0

            row = await db.fetch_one(
                bot_id,
                f"SELECT COALESCE(SUM(unrealized_pnl), 0) as urpnl FROM {pos_table}",
            )
            unrealized = row["urpnl"] if row else 0.0

            today_pnl = closed_pnl + unrealized

            row = await db.fetch_one(
                bot_id,
                "SELECT COALESCE(SUM(pnl), 0) as equity "
                "FROM trades WHERE pnl IS NOT NULL",
            )
            equity = row["equity"] if row else 0.0

        # Open positions count
        row = await db.fetch_one(
            bot_id, f"SELECT COUNT(*) as cnt FROM {pos_table}",
        )
        open_pos = row["cnt"] if row else 0

        # Signals today
        row = await db.fetch_one(
            bot_id,
            f"SELECT COUNT(*) as cnt FROM {sig_table} "
            f"WHERE date(created_at) = date('now')",
        )
        signals_today = row["cnt"] if row else 0

        # Last signal time
        row = await db.fetch_one(
            bot_id,
            f"SELECT created_at FROM {sig_table} ORDER BY created_at DESC LIMIT 1",
        )
        last_signal = row["created_at"] if row else None

        # Bot status
        if db.has_table(bot_id, "bot_state"):
            status = await db.bot_state_status(bot_id)
        else:
            status = db.bot_status(bot_id, last_signal)

        today_pnl_pct = (today_pnl / equity * 100) if equity else 0.0

        bots.append(
            BotOverview(
                id=bot_id,
                name=cfg.name,
                asset_class=cfg.asset_class,
                equity=round(equity, 2),
                today_pnl=round(today_pnl, 2),
                today_pnl_pct=round(today_pnl_pct, 2),
                open_positions=open_pos,
                signals_today=signals_today,
                status=status,
                last_signal=last_signal,
            )
        )

    total_equity = sum(b.equity for b in bots)
    total_pnl = sum(b.today_pnl for b in bots)
    total_pnl_pct = (total_pnl / total_equity * 100) if total_equity else 0.0

    combined = CombinedOverview(
        total_equity=round(total_equity, 2),
        today_pnl=round(total_pnl, 2),
        today_pnl_pct=round(total_pnl_pct, 2),
        open_positions=sum(b.open_positions for b in bots),
        signals_today=sum(b.signals_today for b in bots),
    )

    return OverviewResponse(combined=combined, bots=bots)
