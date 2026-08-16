"""Shared test fixtures for the Sanchaya test suite."""

from collections.abc import Callable
from typing import Any

import pytest

from sanchaya.config import Settings


@pytest.fixture
def make_settings() -> Callable[..., Settings]:
    """Return a factory that builds hermetic Settings with test defaults."""

    def _make(**overrides: Any) -> Settings:
        defaults: dict[str, Any] = {
            "kite_api_key": "test_key",
            "kite_api_secret": "test_secret",
        }
        # _env_file is a valid runtime kwarg mypy can't see (dynamic).
        return Settings(_env_file=None, **{**defaults, **overrides})

    return _make
