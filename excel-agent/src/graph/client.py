from __future__ import annotations
import logging
import time
from typing import Any
import httpx
import msal

logger = logging.getLogger(__name__)

GRAPH_BASE = "https://graph.microsoft.com/v1.0"
GRAPH_SCOPES = ["https://graph.microsoft.com/.default"]


class GraphClient:
    def __init__(
        self,
        client_id: str,
        tenant_id: str,
        username: str,
        password: str,
    ) -> None:
        self._app = msal.PublicClientApplication(
            client_id=client_id,
            authority=f"https://login.microsoftonline.com/{tenant_id}",
        )
        self._username = username
        self._password = password
        self._token: str | None = None
        self._token_expires_at: float = 0.0

    def _acquire_token(self) -> str:
        result = self._app.acquire_token_by_username_password(
            username=self._username,
            password=self._password,
            scopes=GRAPH_SCOPES,
        )
        if "access_token" not in result:
            error = result.get("error_description", result.get("error", "Unknown"))
            raise RuntimeError(f"MSAL token acquisition failed: {error}")
        self._token = result["access_token"]
        expires_in = result.get("expires_in", 3600)
        self._token_expires_at = time.monotonic() + expires_in - 60
        return self._token

    def _get_token(self) -> str:
        if self._token is None or time.monotonic() >= self._token_expires_at:
            self._acquire_token()
        return self._token  # type: ignore[return-value]

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._get_token()}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    async def get(self, path: str, params: dict | None = None) -> Any:
        url = f"{GRAPH_BASE}{path}"
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=self._headers(), params=params)
            if response.status_code == 401:
                self._token = None
                response = await client.get(url, headers=self._headers(), params=params)
            response.raise_for_status()
            return response.json()
