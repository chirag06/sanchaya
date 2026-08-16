"""Tests for Kite authentication behavior."""

from collections.abc import Callable

from sanchaya.config import Settings
from sanchaya.data.kite_auth import KiteAuthManager


def test_compute_checksum(make_settings: Callable[..., Settings]) -> None:
    settings = make_settings(
        kite_api_key="key123",
        kite_api_secret="secret456",
    )
    manager = KiteAuthManager(settings)

    checksum = manager._compute_checksum("reqtok789")

    assert checksum == ("a25c03ed95b7174b89469edb6a36c7fd9c21f01325a6831f8190d9e658eb8fc1")
