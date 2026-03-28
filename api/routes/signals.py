"""GET /api/signals — recent signal activity across all bots."""

from __future__ import annotations

from fastapi import APIRouter, Query

import database as db
from models import Signal, SignalsResponse

router = APIRouter(prefix="/api")


@router.get("/signals", response_model=SignalsResponse)
async def get_signals(
    limit: int = Query(50, ge=1, le=200),
    bot: str | None = Query(None, description="Filter by bot_id"),
) -> SignalsResponse:
    signals: list[Signal] = []

    bot_ids = [bot] if bot and bot in db.settings.bots else list(db.settings.bots)

    for bot_id in bot_ids:
        cfg = db.bot_config(bot_id)
        sym = db.col(bot_id, "signals", "symbol")
        dir_ = db.col(bot_id, "signals", "direction")

        rows = await db.fetch_all(
            bot_id,
            f"SELECT id, {sym}, {dir_}, score, source, created_at "
            f"FROM signals ORDER BY created_at DESC LIMIT ?",
            (limit,),
        )

        for r in rows:
            signals.append(
                Signal(
                    id=r["id"],
                    bot_id=bot_id,
                    bot_name=cfg.name,
                    symbol=r["symbol"],
                    direction=r.get("direction", ""),
                    score=r.get("score"),
                    source=r.get("source"),
                    created_at=r.get("created_at"),
                )
            )

    signals.sort(key=lambda s: s.created_at or "", reverse=True)
    signals = signals[:limit]

    return SignalsResponse(signals=signals, count=len(signals))
