"""Tests for sanchaya.config module."""

import pytest
from pydantic import ValidationError

from sanchaya.config import (
    Environment,
    Settings,
    TradingMode,
    get_settings,
)


def test_settings_defaults_are_safe() -> None:
    """A freshly constructed Settings must default to safe values."""
    settings = Settings()
    assert settings.environment == Environment.DEVELOPMENT
    assert settings.trading_mode == TradingMode.PAPER
    assert settings.is_live() is False


def test_trading_mode_live_is_detected() -> None:
    """is_live() must return True only when trading_mode is LIVE."""
    settings = Settings(trading_mode=TradingMode.LIVE)
    assert settings.is_live() is True


def test_get_settings_returns_same_instance() -> None:
    """get_settings() is cached — repeated calls return the same object."""
    first = get_settings()
    second = get_settings()
    assert first is second


def test_invalid_trading_mode_rejected() -> None:
    """An invalid trading_mode value must raise a validation error."""
    with pytest.raises(ValidationError):
        Settings(trading_mode="banana")  # type: ignore[arg-type]
