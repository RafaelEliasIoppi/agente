from __future__ import annotations
import asyncio
import logging
import time
from pathlib import Path
from typing import Any
import httpx
import msal

logger = logging.getLogger(__name__)

GRAPH_BASE = "https://graph.microsoft.com/v1.0"
GRAPH_SCOPES = ["https://graph.microsoft.com/Files.Read.All", "https://graph.microsoft.com/Sites.Read.All"]


class GraphClient:
    def __init__(
        self,
        client_id: str,
        tenant_id: str,
        token_cache_path: Path,
    ) -> None:
        self._client_id = client_id
        self._authority = f"https://login.microsoftonline.com/{tenant_id}"
        self._token_cache_path = token_cache_path
        self._token: str | None = None
        self._token_expires_at: float = 0.0

        self._cache = msal.SerializableTokenCache()
        if token_cache_path.exists():
            self._cache.deserialize(token_cache_path.read_text(encoding="utf-8"))

        self._app = msal.PublicClientApplication(
            client_id=client_id,
            authority=self._authority,
            token_cache=self._cache,
        )

    def _save_cache(self) -> None:
        if self._cache.has_state_changed:
            self._token_cache_path.parent.mkdir(parents=True, exist_ok=True)
            self._token_cache_path.write_text(self._cache.serialize(), encoding="utf-8")
            logger.debug("Token cache saved")

    def _acquire_token_sync(self) -> str:
        # 1. Tenta renovar silenciosamente via refresh token
        accounts = self._app.get_accounts()
        if accounts:
            result = self._app.acquire_token_silent(GRAPH_SCOPES, account=accounts[0])
            if result and "access_token" in result:
                self._save_cache()
                return result["access_token"]

        # 2. Device Code Flow — só chega aqui se não houver cache válido
        flow = self._app.initiate_device_flow(scopes=GRAPH_SCOPES)
        if "user_code" not in flow:
            raise RuntimeError(
                f"Falha ao iniciar Device Code Flow: {flow.get('error_description', flow)}"
            )

        print("\n" + "=" * 60)
        print("  AUTENTICAÇÃO MICROSOFT NECESSÁRIA")
        print(f"  1. Acesse: {flow['verification_uri']}")
        print(f"  2. Digite o código: {flow['user_code']}")
        print(f"  3. Aguardando login... (expira em {flow.get('expires_in', 900)}s)")
        print("=" * 60 + "\n")

        result = self._app.acquire_token_by_device_flow(flow)  # bloqueia até o login

        if "access_token" not in result:
            raise RuntimeError(
                f"Autenticação falhou: {result.get('error_description', result.get('error'))}"
            )

        self._save_cache()
        logger.info("Autenticação via Device Code Flow concluída com sucesso")
        return result["access_token"]

    def _get_token(self) -> str:
        if self._token is None or time.monotonic() >= self._token_expires_at:
            self._token = self._acquire_token_sync()
            self._token_expires_at = time.monotonic() + 3500  # ~58 min
        return self._token

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._get_token()}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    async def get(self, path: str, params: dict | None = None) -> Any:
        url = f"{GRAPH_BASE}{path}"
        # _get_token pode bloquear (device flow) — rodar em thread para não travar o event loop
        headers = await asyncio.to_thread(self._headers)
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=headers, params=params)
            if response.status_code == 401:
                self._token = None
                headers = await asyncio.to_thread(self._headers)
                response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
