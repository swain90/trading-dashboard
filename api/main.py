"""FastAPI app — unified dashboard API for 3 trading bots."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

import database as db
from config import settings
from routes import all_routers


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    await db.open_all()
    yield
    await db.close_all()


app = FastAPI(
    title="Trading Command Center",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["X-API-Key"],
)


# Auth dependency — applied to all routes except /api/health
async def verify_api_key(request: Request) -> None:
    if request.url.path == "/api/health":
        return
    key = request.headers.get("X-API-Key")
    if not settings.api_key:
        return  # No key configured = no auth (dev mode)
    if key != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")


# Register all routers with auth dependency
for router in all_routers:
    app.include_router(router, dependencies=[Depends(verify_api_key)])
