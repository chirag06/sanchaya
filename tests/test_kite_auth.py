"""Tests for Kite authentication behavior."""

from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import httpx
import pytest
import respx

from sanchaya.config import Settings
from sanchaya.data.kite_auth import KiteAuthManager, TokenExpiredError
from sanchaya.data.kite_models import KiteSessionData


def test_compute_checksum(make_settings: Callable[..., Settings]) -> None:
    settings = make_settings(
        kite_api_key="key123",
        kite_api_secret="secret456",
    )
    manager = KiteAuthManager(settings)

    checksum = manager._compute_checksum("reqtok789")

    assert checksum == ("a25c03ed95b7174b89469edb6a36c7fd9c21f01325a6831f8190d9e658eb8fc1")


def test_login_url(make_settings: Callable[..., Settings]) -> None:
    """Login URL must target Kite's login endpoint with v and api_key params."""
    settings = make_settings(kite_api_key="key123")
    manager = KiteAuthManager(settings)

    parsed = urlparse(manager.login_url())

    assert parsed.scheme == "https"
    assert parsed.netloc == "kite.zerodha.com"
    assert parsed.path == "/connect/login"
    assert parse_qs(parsed.query) == {"v": ["3"], "api_key": ["key123"]}


def test_session_round_trip(make_settings: Callable[..., Settings], tmp_path: Path) -> None:
    """A stored session must load back, and the file must be owner-only."""
    settings = make_settings(data_cache_dir=tmp_path)
    manager = KiteAuthManager(
        settings,
        now_fn=lambda: datetime(2026, 6, 14, 10, 0),
    )
    session = KiteSessionData(
        user_id="AB1234",
        user_name="Test User",
        access_token="tok_abc123",
        login_time=datetime(2026, 6, 14, 9, 15),
    )

    manager.store_session(session)
    token = manager.get_access_token()

    assert token == "tok_abc123"
    file_mode = (tmp_path / "kite_session.json").stat().st_mode & 0o777
    assert file_mode == 0o600


@pytest.mark.parametrize(
    ("login_time", "now", "should_be_valid"),
    [
        # Normal login (after 6 AM) → expires 6 AM next day
        (datetime(2026, 6, 14, 9, 15), datetime(2026, 6, 15, 5, 59), True),
        (datetime(2026, 6, 14, 9, 15), datetime(2026, 6, 15, 6, 1), False),
        # Pre-6-AM login → expires SAME day at 6 AM (your own edge case)
        (datetime(2026, 6, 14, 5, 0), datetime(2026, 6, 14, 5, 30), True),
        (datetime(2026, 6, 14, 5, 0), datetime(2026, 6, 14, 6, 1), False),
    ],
)
def test_token_expiry_boundaries(
    make_settings: Callable[..., Settings],
    tmp_path: Path,
    login_time: datetime,
    now: datetime,
    should_be_valid: bool,
) -> None:
    """Tokens die at 6 AM after login; pre-6-AM logins die same day."""
    settings = make_settings(data_cache_dir=tmp_path)
    manager = KiteAuthManager(settings, now_fn=lambda: now)
    session = KiteSessionData(
        user_id="AB1234",
        user_name="Test User",
        access_token="tok_abc123",
        login_time=login_time,
    )
    manager.store_session(session)

    if should_be_valid:
        assert manager.get_access_token() == "tok_abc123"
    else:
        with pytest.raises(TokenExpiredError):
            manager.get_access_token()


def test_missing_session_file_raises(
    make_settings: Callable[..., Settings], tmp_path: Path
) -> None:
    """No stored session must raise TokenExpiredError, not FileNotFoundError."""
    settings = make_settings(data_cache_dir=tmp_path)
    manager = KiteAuthManager(settings, now_fn=lambda: datetime(2026, 6, 14, 10, 0))

    with pytest.raises(TokenExpiredError):
        manager.get_access_token()


@respx.mock
def test_exchange_token_success(make_settings: Callable[..., Settings]) -> None:
    """A successful exchange must parse Kite's envelope into KiteSessionData."""
    route = respx.post("https://api.kite.trade/session/token").mock(
        return_value=httpx.Response(
            200,
            json={
                "status": "success",
                "data": {
                    "user_id": "AB1234",
                    "user_name": "Test User",
                    "access_token": "tok_from_kite",
                    "login_time": "2026-08-17 09:15:00",
                },
            },
        )
    )
    settings = make_settings(kite_api_key="key123", kite_api_secret="secret456")
    manager = KiteAuthManager(settings)

    session = manager.exchange_token("reqtok789")

    assert session.user_id == "AB1234"
    assert session.access_token.get_secret_value() == "tok_from_kite"
    assert route.called
    sent = route.calls.last.request
    assert b"checksum=" in sent.content
