"""Route aggregation — all API routers collected here."""

from routes.health import router as health_router
from routes.overview import router as overview_router
from routes.positions import router as positions_router
from routes.signals import router as signals_router
from routes.trades import router as trades_router

all_routers = [
    overview_router,
    positions_router,
    signals_router,
    trades_router,
    health_router,
]
