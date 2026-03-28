# 📊 Trading Command Center — SuperClaude Execution Playbook

3-phase weekend build: Backend API → React Frontend → Deploy.

---

## Phase 1 — Backend API (Saturday morning, ~2 sessions)

### Design
```
/sc:design "FastAPI backend that reads 3 SQLite databases (Whale Watcher equities, 
Commodity Hunter futures, Whale Watcher Crypto) and exposes a unified REST API. 
Read-only access, API key auth, endpoints for overview/positions/signals/trades/health. 
Must handle missing DBs gracefully and normalize schema differences 
(WW uses 'ticker', others use 'symbol')." --persona-architect
```

### Implement
```
/sc:implement "Phase 1 per CURRENT_TASK.md: FastAPI app with 5 route modules 
(overview, positions, signals, trades, health), bot registry config, read-only 
async SQLite connections to 3 databases, API key middleware, Pydantic response 
models. Handle missing DBs gracefully. Include Dockerfile." --tdd --persona-backend
```

### Test & Deploy
```
/sc:test --coverage

# Deploy to droplet
scp -r api/ root@droplet:/opt/trading-dashboard/
ssh root@droplet "cd /opt/trading-dashboard && docker-compose up -d"

# Verify
curl -H "X-API-Key: your-key" http://droplet-ip:8090/api/health
```

---

## Phase 2 — React Frontend (Saturday afternoon, ~2 sessions)

### Design
```
/sc:design "React dashboard for 3 trading bots. Components: 
OverviewCards (P&L per bot + combined), PositionsTable (all open positions), 
SignalFeed (scrolling signal activity), TradeHistory (win/loss table with stats), 
BotStatus (health indicators). Dark theme, auto-refresh every 30s, 
mobile-responsive. Tailwind CSS." --persona-frontend
```

### Implement
```
/sc:implement "Phase 2: React frontend with Tailwind. 
5 components: OverviewCards, PositionsTable, SignalFeed, TradeHistory, BotStatus.
useApi hook that polls backend every 30s with API key header.
Dark theme with green/red P&L colors. Color-coded bot badges 
(blue=equities, orange=futures, purple=crypto).
Mobile-first responsive layout. Deploy config for Vercel." --persona-frontend
```

---

## Phase 3 — Deploy & Polish (Saturday evening, ~1 session)

### Deploy Frontend
```bash
cd web
npm install
npx vercel --prod
# Set environment variable: VITE_API_URL=https://your-droplet:8090
# Set environment variable: VITE_API_KEY=your-key
```

### Secure the API
```bash
# On droplet — nginx reverse proxy with HTTPS
sudo apt install nginx certbot python3-certbot-nginx
# Configure nginx to proxy 8090 with SSL
# Or use Cloudflare tunnel (free) for HTTPS without opening ports
```

### Polish
```
/sc:improve web/src/ --persona-frontend
```

---

## Quick Reference: What Each Endpoint Returns

### GET /api/overview
Combined equity, today's P&L, per-bot breakdown with status indicators.

### GET /api/positions
All open positions across 3 bots. Each row shows: bot, symbol, side, 
size, entry price, current price, unrealized P&L, stop loss, take profit.

### GET /api/signals?limit=50
Most recent signals across all bots. Each row: bot, source, symbol, 
direction, score, timestamp. Sortable by time or score.

### GET /api/trades?days=7
Closed trades with P&L. Summary stats: total trades, win rate, 
total P&L, best trade, worst trade, average hold time.

### GET /api/health  
Per-bot: running/stopped, uptime, IB/KuCoin connected, last signal time,
open positions count, today's trade count.
