"""Tests for sanchaya.config module."""

from collections.abc import Callable

import pytest
from pydantic import ValidationError

from sanchaya.config import Environment, Settings, TradingMode, get_settings


def test_settings_defaults_are_safe(make_settings: Callable[..., Settings]) -> None:
    """A freshly constructed Settings must default to safe values."""
    settings = make_settings()
    assert settings.environment == Environment.DEVELOPMENT
    assert settings.trading_mode == TradingMode.PAPER
    assert settings.is_live() is False


def test_trading_mode_live_is_detected(make_settings: Callable[..., Settings]) -> None:
    """is_live() must return True only when trading_mode is LIVE."""
    settings = make_settings(trading_mode=TradingMode.LIVE)
    assert settings.is_live() is True


def test_get_settings_returns_same_instance(monkeypatch: pytest.MonkeyPatch) -> None:
    """get_settings() is cached — repeated calls return the same object."""
    monkeypatch.setenv("KITE_API_KEY", "test_key")
    monkeypatch.setenv("KITE_API_SECRET", "test_secret")
    get_settings.cache_clear()
    try:
        first = get_settings()
        second = get_settings()
        assert first is second
    finally:
        get_settings.cache_clear()


def test_invalid_trading_mode_rejected(make_settings: Callable[..., Settings]) -> None:
    """An invalid trading_mode value must raise a validation error."""
    with pytest.raises(ValidationError):
        make_settings(trading_mode="banana")


def test_kite_secret_is_masked(make_settings: Callable[..., Settings]) -> None:
    settings = make_settings()
    assert "test_secret" not in str(settings.kite_api_secret)
    assert settings.kite_api_secret.get_secret_value() == "test_secret"


def test_missing_kite_credentials_rejected() -> None:
    """Settings must fail at construction if Kite credentials are absent."""
    with pytest.raises(ValidationError):
        Settings(_env_file=None)
