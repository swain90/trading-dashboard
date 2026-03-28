"""Pydantic response models for all API endpoints."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


# --- Overview ---

class BotOverview(BaseModel):
    id: str
    name: str
    asset_class: str
    equity: float
    today_pnl: float
    today_pnl_pct: float
    open_positions: int
    signals_today: int
    status: str  # "running" | "stopped" | "unavailable"
    last_signal: datetime | None


class CombinedOverview(BaseModel):
    total_equity: float
    today_pnl: float
    today_pnl_pct: float
    open_positions: int
    signals_today: int


class OverviewResponse(BaseModel):
    combined: CombinedOverview
    bots: list[BotOverview]


# --- Positions ---

class Position(BaseModel):
    id: int
    bot_id: str
    bot_name: str
    symbol: str
    side: str
    size: float
    entry_price: float
    current_price: float | None
    unrealized_pnl: float | None
    stop_loss: float | None
    take_profit: float | None
    opened_at: datetime | None


class PositionsResponse(BaseModel):
    positions: list[Position]
    count: int


# --- Signals ---

class Signal(BaseModel):
    id: int
    bot_id: str
    bot_name: str
    symbol: str
    direction: str
    score: float | None
    source: str | None
    created_at: datetime | None


class SignalsResponse(BaseModel):
    signals: list[Signal]
    count: int


# --- Trades ---

class Trade(BaseModel):
    id: int
    bot_id: str
    bot_name: str
    symbol: str
    side: str
    quantity: float | None
    entry_price: float | None
    exit_price: float | None
    pnl: float | None
    opened_at: datetime | None
    closed_at: datetime | None


class TradeStats(BaseModel):
    total_trades: int
    wins: int
    losses: int
    win_rate: float
    total_pnl: float
    best_trade: float
    worst_trade: float
    avg_pnl: float


class TradesResponse(BaseModel):
    trades: list[Trade]
    stats: TradeStats
    count: int


# --- Health ---

class BotHealth(BaseModel):
    id: str
    name: str
    status: str  # "running" | "stopped" | "unavailable"
    db_connected: bool
    last_signal: datetime | None
    open_positions: int
    trades_today: int


class HealthResponse(BaseModel):
    status: str
    bots: list[BotHealth]
