"""Centralized configuration for Sanchaya.

All application settings live here as a single validated Settings object.
Settings are loaded from environment variables (and a .env file in development).

Usage:
    from sanchaya.config import get_settings

    settings = get_settings()
    print(settings.environment)
"""

from enum import StrEnum
from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(StrEnum):
    """The runtime environment Sanchaya is operating in."""

    DEVELOPMENT = "development"
    PAPER = "paper"
    LIVE = "live"


class TradingMode(StrEnum):
    """Whether orders are simulated or sent to a real broker.

    PAPER  — orders are simulated; no real money moves.
    LIVE   — orders are sent to the broker; real money moves.

    This is the single most important flag in the system. It defaults to
    PAPER and must be explicitly set to LIVE.
    """

    PAPER = "paper"
    LIVE = "live"


class Settings(BaseSettings):
    """Application settings, loaded from environment variables.

    pydantic-settings reads each field from an environment variable of the
    same name (case-insensitive). Missing required fields raise an error at
    startup — failing fast is better than failing mid-trade.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- Environment ---
    environment: Environment = Field(
        default=Environment.DEVELOPMENT,
        description="Runtime environment.",
    )

    # --- Trading mode: the safety-critical flag ---
    trading_mode: TradingMode = Field(
        default=TradingMode.PAPER,
        description="PAPER (simulated) or LIVE (real money). Defaults to PAPER.",
    )

    # --- Paths ---
    data_cache_dir: Path = Field(
        default=Path("./cache"),
        description="Directory for cached market data.",
    )
    logs_dir: Path = Field(
        default=Path("./logs"),
        description="Directory for log files.",
    )

    # --- Logging ---
    log_level: str = Field(
        default="INFO",
        description="Logging level: DEBUG, INFO, WARNING, ERROR.",
    )

    def is_live(self) -> str:
        """Return True if the system is in live (real-money) trading mode."""
        return self.trading_mode == TradingMode.LIVE


@lru_cache
def get_settings() -> Settings:
    """Return the application settings, loaded once and cached.

    The lru_cache decorator ensures Settings is constructed only once per
    process. Every caller gets the same instance.

    Returns:
        The validated Settings object.
    """
    return Settings()
