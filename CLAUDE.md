# Trading Command Center — Unified Dashboard

## Identity
A unified dashboard for monitoring 3 autonomous trading bots: Whale Watcher (US equities), Commodity Hunter (micro futures), and Whale Watcher Crypto (KuCoin futures). Displays live P&L, open positions, signal activity, and trade history across all bots from a single interface.

## Tech Stack
- **Backend**: FastAPI (Python 3.12) — reads 3 SQLite databases, exposes unified REST API
- **Frontend**: React + Tailwind CSS — deployed to Vercel (free tier)
- **Auth**: API key in header (personal dashboard, not multi-user)
- **Deployment**: Backend on existing DigitalOcean droplet (port 8090), frontend on Vercel

## Architecture
```
Droplet:
  /data/trading.db         → Whale Watcher (equities)
  /data/commodity.db       → Commodity Hunter (futures)
  /data/crypto.db          → Whale Watcher Crypto (KuCoin)
          ↓
  FastAPI Hub (port 8090)  → Reads all 3 DBs, tags by bot
          ↓ HTTPS
  React on Vercel          → Polls every 30s, renders dashboard
```

## Backend Structure
```
api/
├── main.py               # FastAPI app, CORS, auth middleware
├── config.py             # DB paths, API key, bot names
├── database.py           # Read-only SQLite connections to all 3 DBs
├── routes/
│   ├── overview.py       # GET /api/overview — combined P&L, equity, bot status
│   ├── positions.py      # GET /api/positions — open positions across all bots
│   ├── signals.py        # GET /api/signals — recent signal activity feed
│   ├── trades.py         # GET /api/trades — trade history with stats
│   └── health.py         # GET /api/health — bot health status
├── models.py             # Pydantic response models
└── Dockerfile
```

## Frontend Structure
```
web/
├── src/
│   ├── App.jsx           # Main layout with auto-refresh
│   ├── components/
│   │   ├── OverviewCards.jsx    # P&L cards per bot + combined
│   │   ├── PositionsTable.jsx   # Open positions across all bots
│   │   ├── SignalFeed.jsx       # Real-time signal activity
│   │   ├── TradeHistory.jsx     # Trade log with win/loss
│   │   └── BotStatus.jsx       # Health indicators per bot
│   ├── hooks/
│   │   └── useApi.js           # Polling hook with refresh interval
│   └── lib/
│       └── api.js              # API client with auth header
├── package.json
├── tailwind.config.js
└── vercel.json
```

## API Endpoints
| Method | Path | Description |
|--------|------|-------------|
| GET | /api/overview | Combined equity, P&L today, P&L all-time per bot |
| GET | /api/positions | All open positions tagged by bot |
| GET | /api/signals?limit=50 | Recent signals across all bots |
| GET | /api/trades?days=7 | Trade history with P&L, win/loss |
| GET | /api/health | Bot status: uptime, connected, last signal time |

## Critical Rules
- **READ-ONLY** — dashboard never writes to any database
- **API key auth** — simple header check, not full auth system
- Backend reads SQLite files directly (no network DB connection needed)
- Frontend polls, no WebSocket (simpler, Vercel-compatible)
- All timestamps displayed in user's local timezone (convert from UTC)

## Database Mapping
Bots use SQLAlchemy 2.0 with varying schemas. The API normalizes all to a unified format:
| Bot | DB Path | Signal table | Trade table | Position table |
|-----|---------|-------------|-------------|----------------|
| Whale Watcher | /data/ww/trading.db | signals (ticker) | trades | positions |
| Commodity Hunter | /data/ch/commodity.db | signals (symbol) | trades | positions |
| Crypto | /data/crypto/crypto.db | signals (symbol) | trades | positions |
| Forecast Maker | /data/fm/forecast_maker.db | quotes (symbol, side) | fills (filled_at) | inventory (quantity, avg_cost) |

Note: WW uses "ticker", others use "symbol". FM has a completely different schema:
- quotes→signals, fills→trades, inventory→positions (table_map in BotConfig)
- P&L from daily_pnl table, status from bot_state table
- Column aliases: side→direction, quantity→size, avg_cost→entry_price, filled_at→closed_at

## SuperClaude Integration
Preferred workflow: /sc:design → /sc:implement --tdd → /sc:test
See SUPERCLAUDE_PLAYBOOK.md for build sequence.

## Context Tiers
- **Tier 1**: This file
- **Tier 2**: CURRENT_TASK.md
