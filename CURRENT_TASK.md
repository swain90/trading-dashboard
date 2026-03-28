# Completed: Phase 1 — Backend API

## Objective
Build the FastAPI backend that reads all 3 bot SQLite databases and exposes a unified REST API. Deploy on the DigitalOcean droplet alongside the trading bots.

## Definition of Done
- [ ] FastAPI app starts on port 8090
- [ ] API key auth middleware rejects unauthorized requests
- [ ] /api/overview returns combined equity and P&L per bot
- [ ] /api/positions returns all open positions tagged by bot name
- [ ] /api/signals returns recent signals across all bots (paginated)
- [ ] /api/trades returns trade history with win/loss stats (filterable by days)
- [ ] /api/health returns bot status (last signal time, connection state)
- [ ] CORS configured for Vercel frontend domain
- [ ] All endpoints handle missing/empty databases gracefully
- [ ] Dockerfile builds and runs
- [ ] docker-compose.yml mounts all 3 DB volumes read-only
- [ ] 20+ tests passing

## Files to Create

### Backend (api/)
```
api/
├── main.py              # FastAPI app, CORS, auth, lifespan
├── config.py            # Settings: DB paths, API key, bot registry
├── database.py          # Read-only async connections to 3 SQLite DBs
├── models.py            # Pydantic response schemas
├── routes/
│   ├── __init__.py
│   ├── overview.py      # GET /api/overview
│   ├── positions.py     # GET /api/positions
│   ├── signals.py       # GET /api/signals
│   ├── trades.py        # GET /api/trades
│   └── health.py        # GET /api/health
├── Dockerfile
├── requirements.txt     # FastAPI, uvicorn, aiosqlite, pydantic
└── tests/
    ├── conftest.py
    ├── test_overview.py
    ├── test_positions.py
    ├── test_signals.py
    └── test_trades.py
```

## Implementation Details

### Bot Registry (config.py)
```python
BOTS = {
    "whale_watcher": {
        "name": "Whale Watcher",
        "db_path": "/data/ww/trading.db",
        "asset_class": "equities",
        "ticker_field": "ticker",  # WW uses "ticker" not "symbol"
    },
    "commodity_hunter": {
        "name": "Commodity Hunter",
        "db_path": "/data/ch/commodity.db",
        "asset_class": "futures",
        "ticker_field": "symbol",
    },
    "crypto": {
        "name": "Whale Watcher Crypto",
        "db_path": "/data/crypto/crypto.db",
        "asset_class": "crypto",
        "ticker_field": "symbol",
    },
}
```

### Overview Response
```json
{
  "combined": {
    "total_equity": 156234.50,
    "today_pnl": 342.18,
    "today_pnl_pct": 0.22,
    "open_positions": 5,
    "signals_today": 23
  },
  "bots": [
    {
      "id": "whale_watcher",
      "name": "Whale Watcher",
      "equity": 136200.00,
      "today_pnl": 215.40,
      "open_positions": 3,
      "status": "running",
      "last_signal": "2026-03-27T14:30:00Z"
    },
    ...
  ]
}
```

### Auth Middleware
```python
# Simple API key check — not multi-user, just prevents random access
async def verify_api_key(request: Request):
    key = request.headers.get("X-API-Key")
    if key != settings.api_key:
        raise HTTPException(401, "Invalid API key")
```

### Database Access
- Open each SQLite in READ-ONLY mode (uri=True, ?mode=ro)
- Create connections on startup, close on shutdown
- Handle missing DB files gracefully (bot not yet deployed)
- Normalize WW "ticker" → "symbol" in queries

## Docker Compose
```yaml
services:
  dashboard-api:
    build: ./api
    ports:
      - "8090:8090"
    volumes:
      - whale-watcher_trading-data:/data/ww:ro
      - commodity-hunter_commodity-data:/data/ch:ro
      - crypto-data:/data/crypto:ro
    environment:
      API_KEY: ${DASHBOARD_API_KEY}
```

## SuperClaude Commands
```bash
/sc:design "unified trading dashboard API reading 3 SQLite databases" --persona-architect
/sc:implement "Phase 1 per CURRENT_TASK.md" --tdd --persona-backend
/sc:test --coverage
```
# Current Task: Phase 2: React frontend with Tailwind dark theme.
5 components: OverviewCards, PositionsTable, SignalFeed, TradeHistory, BotStatus.
useApi hook polling every 30s. Color-coded bot badges (blue=equities, orange=futures, purple=crypto).
Green/red P&L. Mobile-responsive. Vercel deploy config.