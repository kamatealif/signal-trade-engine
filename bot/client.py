"""Binance Futures Testnet client wrapper."""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import time
from typing import Any
from urllib import error, parse, request

from bot.errors import BinanceAPIError, NetworkError


class BinanceFuturesClient:
    """Minimal client for Binance Futures (USDT-M) signed endpoints."""

    def __init__(
        self,
        *,
        api_key: str,
        api_secret: str,
        base_url: str = "https://testnet.binancefuture.com",
        timeout: int = 15,
        recv_window: int = 5000,
        logger: logging.Logger | None = None,
    ) -> None:
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.recv_window = recv_window
        self.logger = logger or logging.getLogger("trading_bot")

    def place_order(self, *, params: dict[str, str]) -> dict[str, Any]:
        return self._signed_request(method="POST", path="/fapi/v1/order", params=params)

    def _signed_request(
        self, *, method: str, path: str, params: dict[str, str]
    ) -> dict[str, Any]:
        payload = dict(params)
        payload["timestamp"] = str(int(time.time() * 1000))
        payload["recvWindow"] = str(self.recv_window)

        query_string = parse.urlencode(payload)
        signature = hmac.new(
            self.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        signed_query = f"{query_string}&signature={signature}"
        url = f"{self.base_url}{path}?{signed_query}"

        safe_payload = dict(payload)
        self.logger.info("api_request method=%s path=%s payload=%s", method, path, safe_payload)
        return self._send_request(method=method, url=url, path=path)

    def _send_request(self, *, method: str, url: str, path: str) -> dict[str, Any]:
        req = request.Request(
            url=url,
            method=method.upper(),
            headers={"X-MBX-APIKEY": self.api_key},
        )

        try:
            with request.urlopen(req, timeout=self.timeout) as resp:
                body = resp.read().decode("utf-8")
                self.logger.info("api_response path=%s status=%s body=%s", path, resp.status, body)
                return self._parse_json(body, status_code=resp.status)
        except error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            self.logger.error(
                "api_http_error path=%s status=%s body=%s",
                path,
                exc.code,
                body,
            )
            self._raise_binance_error(body=body, status_code=exc.code)
            raise  # pragma: no cover
        except error.URLError as exc:
            self.logger.error("api_network_error path=%s reason=%s", path, exc.reason)
            raise NetworkError(f"Network error while calling Binance API: {exc.reason}") from exc

    def _parse_json(self, body: str, *, status_code: int) -> dict[str, Any]:
        try:
            data = json.loads(body)
        except json.JSONDecodeError as exc:
            raise BinanceAPIError(
                "Binance API returned non-JSON response",
                status_code=status_code,
            ) from exc

        if not isinstance(data, dict):
            raise BinanceAPIError(
                "Unexpected Binance API response format",
                status_code=status_code,
            )
        return data

    def _raise_binance_error(self, *, body: str, status_code: int) -> None:
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            raise BinanceAPIError(
                f"Binance API request failed with HTTP {status_code}",
                status_code=status_code,
            )

        if isinstance(data, dict):
            code = data.get("code")
            message = str(data.get("msg", f"Binance API request failed with HTTP {status_code}"))
            parsed_code = code if isinstance(code, int) else None
            raise BinanceAPIError(
                message,
                status_code=status_code,
                error_code=parsed_code,
            )

        raise BinanceAPIError(
            f"Binance API request failed with HTTP {status_code}",
            status_code=status_code,
        )

