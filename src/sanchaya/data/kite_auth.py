import hashlib
import json
import logging
from collections.abc import Callable
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urlencode

import httpx

from sanchaya.config import Settings
from sanchaya.data.kite_models import KiteSessionData, KiteTokenResponse

logger = logging.getLogger(__name__)

KITE_LOGIN_URL = "https://kite.zerodha.com/connect/login"
KITE_SESSION_URL = "https://api.kite.trade/session/token"


class TokenExpiredError(Exception):
    """Raised when no valid Kite session exists (missing or past daily expiry)."""


class KiteAuthManager:
    def __init__(self, settings: Settings, now_fn: Callable[[], datetime] = datetime.now) -> None:
        self._settings = settings
        self._now = now_fn

    @property
    def _session_file(self) -> Path:
        return self._settings.data_cache_dir / "kite_session.json"

    def login_url(self) -> str:
        """
        Construct the kite login url using kite api key
        Returns:
            Kite url for login
        """
        params = {"v": "3", "api_key": self._settings.kite_api_key}
        return f"{KITE_LOGIN_URL}?{urlencode(params)}"

    def _compute_checksum(self, request_token: str) -> str:
        """Compute Kite's session checksum: SHA-256 of key + request_token + secret."""
        secret = self._settings.kite_api_secret.get_secret_value()
        raw = f"{self._settings.kite_api_key}{request_token}{secret}"
        return hashlib.sha256(raw.encode()).hexdigest()

    def exchange_token(self, request_token: str) -> KiteSessionData:
        """Exchange an OAuth request token for a Kite session.
        Implements step 2 of Kite's login flow: computes the SHA-256 checksum
        proving possession of the API secret, POSTs it with the request token
        to Kite's session endpoint, and validates the response at the boundary.

        Args:
            request_token: Short-lived token from the post-login browser
                redirect. Expires within minutes of issue.

        Returns:
            Validated session data, including the access token used to
            authenticate all subsequent Kite API calls.

        Raises:
            httpx.HTTPStatusError: If Kite rejects the exchange (expired or
                already-used request token, bad credentials).
            pydantic.ValidationError: If the response doesn't match the
                expected shape.
        """

        response = httpx.post(
            KITE_SESSION_URL,
            headers={"X-Kite-Version": "3"},
            data={
                "api_key": self._settings.kite_api_key,
                "request_token": request_token,
                "checksum": self._compute_checksum(request_token),
            },
            timeout=10.0,  # explicit, always
        )
        response.raise_for_status()
        session = KiteTokenResponse.model_validate(response.json()).data
        logger.info("Kite token exchange succeeded for user_id=%s", session.user_id)
        return session

    def store_session(self, session: KiteSessionData) -> None:
        payload = {
            "user_id": session.user_id,
            "user_name": session.user_name,
            "access_token": session.access_token.get_secret_value(),
            "login_time": session.login_time.isoformat(),
        }
        self._session_file.parent.mkdir(parents=True, exist_ok=True)
        self._session_file.write_text(json.dumps(payload))
        self._session_file.chmod(0o600)

    def get_access_token(self) -> str:
        if not self._session_file.exists():
            raise TokenExpiredError("No Kite session found — run: sanchaya kite login")

        kite_session_data: KiteSessionData = KiteSessionData.model_validate_json(
            self._session_file.read_text()
        )

        login_time = kite_session_data.login_time
        access_token = kite_session_data.access_token.get_secret_value()

        expiry_time = login_time.replace(hour=6, minute=0, second=0, microsecond=0)

        if login_time >= expiry_time:
            expiry_time += timedelta(days=1)

        # NOTE: naive datetime comparison — assumes both login_time (IST from
        # Kite) and now_fn run in IST. Breaks on a UTC server; fix with proper
        # tz-aware datetimes.
        if self._now() >= expiry_time:
            raise TokenExpiredError("Kite token expired — run: sanchaya kite login")

        return access_token
