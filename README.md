# 📊 Trading Command Center

Unified dashboard for monitoring 3 autonomous trading bots from a single interface.

| Bot | Asset Class | Exchange |
|-----|------------|----------|
| Whale Watcher | US Equities | Interactive Brokers |
| Commodity Hunter | Micro Futures | Interactive Brokers |
| Whale Watcher Crypto | Crypto Futures | KuCoin |

## Features
- **Live P&L** per bot + combined total
- **Open positions** across all 3 bots with unrealized P&L
- **Signal activity feed** — real-time signals as they fire
- **Trade history** with win/loss stats and charts
- **Bot health** — uptime, connection status, last signal time

## Architecture
- **Backend**: FastAPI on DigitalOcean (reads 3 SQLite DBs)
- **Frontend**: React + Tailwind on Vercel (free tier)

## Quick Start

### Backend
```bash
cd api
cp ../.env.example ../.env  # Set DASHBOARD_API_KEY
docker-compose up -d
curl -H "X-API-Key: your-key" http://localhost:8090/api/health
```

### Frontend
```bash
cd web
npm install
# Set VITE_API_URL and VITE_API_KEY in .env.local
npm run dev        # Local development
npx vercel --prod  # Deploy to Vercel
```

## Build Guide
See [SUPERCLAUDE_PLAYBOOK.md](SUPERCLAUDE_PLAYBOOK.md) for the complete build sequence using Claude Code + SuperClaude.

## License
MIT
