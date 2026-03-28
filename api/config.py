"""Configuration: bot registry, settings from environment."""

from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass(frozen=True)
class BotConfig:
    name: str
    db_path: str
    asset_class: str
    ticker_field: str  # "ticker" for WW, "symbol" for others


@dataclass
class Settings:
    api_key: str = ""
    cors_origins: list[str] = field(default_factory=list)
    bots: dict[str, BotConfig] = field(default_factory=dict)

    @classmethod
    def from_env(cls) -> Settings:
        return cls(
            api_key=os.getenv("DASHBOARD_API_KEY", ""),
            cors_origins=[
                o.strip()
                for o in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
                if o.strip()
            ],
            bots={
                "whale_watcher": BotConfig(
                    name="Whale Watcher",
                    db_path=os.getenv("WW_DB_PATH", "/data/ww/trading.db"),
                    asset_class="equities",
                    ticker_field="ticker",
                ),
                "commodity_hunter": BotConfig(
                    name="Commodity Hunter",
                    db_path=os.getenv("CH_DB_PATH", "/data/ch/commodity.db"),
                    asset_class="futures",
                    ticker_field="symbol",
                ),
                "crypto": BotConfig(
                    name="Whale Watcher Crypto",
                    db_path=os.getenv("CRYPTO_DB_PATH", "/data/crypto/crypto.db"),
                    asset_class="crypto",
                    ticker_field="symbol",
                ),
            },
        )


settings = Settings.from_env()
