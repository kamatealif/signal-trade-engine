"""Binance Futures Testnet client wrapper."""

from __future__ import annotations

import logging
from typing import Any

from bot.errors import BinanceAPIError, NetworkError

try:
    from binance.client import Client as BinanceClient
    from binance.exceptions import BinanceAPIException, BinanceRequestException
except ImportError:  # pragma: no cover - validated at runtime
    BinanceClient = None  # type: ignore[assignment]
    BinanceAPIException = Exception  # type: ignore[assignment]
    BinanceRequestException = Exception  # type: ignore[assignment]


class BinanceFuturesClient:
    """Client wrapper using python-binance for USDT-M Futures Testnet."""

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

        if BinanceClient is None:
            raise RuntimeError(
                "python-binance is not installed. Run `uv sync` to install dependencies."
            )

        self._client = BinanceClient(
            api_key=api_key,
            api_secret=api_secret,
            testnet=True,
            requests_params={"timeout": timeout},
        )
        # Ensure futures requests hit the assignment-required testnet host.
        self._client.FUTURES_URL = f"{self.base_url}/fapi"

    def place_order(self, *, params: dict[str, str]) -> dict[str, Any]:
        path = "/fapi/v1/order"
        payload = dict(params)
        payload["recvWindow"] = self.recv_window

        self.logger.info("api_request method=%s path=%s payload=%s", "POST", path, payload)

        try:
            response = self._client.futures_create_order(**payload)
        except BinanceAPIException as exc:
            status_code = getattr(exc, "status_code", None)
            error_code = getattr(exc, "code", None)
            message = getattr(exc, "message", None) or str(exc)
            self.logger.error(
                "api_http_error path=%s status=%s code=%s message=%s",
                path,
                status_code,
                error_code,
                message,
            )
            raise BinanceAPIError(
                message,
                status_code=status_code,
                error_code=error_code if isinstance(error_code, int) else None,
            ) from exc
        except BinanceRequestException as exc:
            message = getattr(exc, "message", None) or str(exc)
            self.logger.error("api_network_error path=%s reason=%s", path, message)
            raise NetworkError(f"Network error while calling Binance API: {message}") from exc
        except Exception as exc:
            self.logger.error("api_unexpected_error path=%s message=%s", path, exc)
            raise NetworkError(f"Unexpected client error while calling Binance API: {exc}") from exc

        self.logger.info("api_response path=%s body=%s", path, response)
        if not isinstance(response, dict):
            raise BinanceAPIError("Unexpected Binance API response format")
        return response
