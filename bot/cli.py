"""CLI entry point for placing Binance Futures testnet orders."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Sequence

from bot.client import BinanceFuturesClient
from bot.errors import BinanceAPIError, NetworkError, ValidationError
from bot.logging_config import configure_logging
from bot.orders import build_order_request, resolve_avg_price


def load_dotenv(env_path: Path, *, override: bool = True) -> None:
    """Load key-value pairs from .env into process environment."""
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export ") :].strip()
        if "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()

        if not key:
            continue
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]

        if override:
            os.environ[key] = value
        else:
            os.environ.setdefault(key, value)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Place BUY/SELL MARKET/LIMIT orders on Binance Futures Testnet (USDT-M)."
    )
    parser.add_argument("--symbol", required=True, help="Trading symbol, e.g. BTCUSDT")
    parser.add_argument("--side", required=True, help="BUY or SELL")
    parser.add_argument("--order-type", required=True, help="MARKET or LIMIT")
    parser.add_argument("--quantity", required=True, help="Order quantity, e.g. 0.001")
    parser.add_argument(
        "--price",
        help="Limit price (required for LIMIT, forbidden for MARKET), e.g. 43000",
    )

    parser.add_argument(
        "--api-key",
        default=None,
        help="Binance API key. Falls back to API_KEY/.env and BINANCE_API_KEY.",
    )
    parser.add_argument(
        "--api-secret",
        default=None,
        help="Binance API secret. Falls back to SECRET_KEY/.env and BINANCE_API_SECRET.",
    )
    parser.add_argument(
        "--base-url",
        default="https://testnet.binancefuture.com",
        help="Binance Futures base URL (default: testnet)",
    )
    parser.add_argument(
        "--log-file",
        default="logs/trading_bot.log",
        help="Log file path (default: logs/trading_bot.log)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=15,
        help="HTTP timeout in seconds (default: 15)",
    )
    parser.add_argument(
        "--recv-window",
        type=int,
        default=5000,
        help="Binance recvWindow in ms (default: 5000)",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    logger = configure_logging(args.log_file)
    load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=True)

    try:
        order_request = build_order_request(
            symbol=args.symbol,
            side=args.side,
            order_type=args.order_type,
            quantity=args.quantity,
            price=args.price,
        )
    except ValidationError as exc:
        logger.error("validation_error message=%s", exc)
        print(f"Input validation failed: {exc}")
        return 2

    api_key = args.api_key or os.getenv("API_KEY") or os.getenv("BINANCE_API_KEY")
    api_secret = args.api_secret or os.getenv("SECRET_KEY") or os.getenv(
        "BINANCE_API_SECRET"
    )
    if not api_key or not api_secret:
        logger.error("missing_credentials")
        print(
            "Missing API credentials. Add API_KEY and SECRET_KEY to .env, or use "
            "--api-key/--api-secret."
        )
        return 2

    print("Order Request Summary")
    print(f"  Symbol: {order_request.symbol}")
    print(f"  Side: {order_request.side}")
    print(f"  Order Type: {order_request.order_type}")
    print(f"  Quantity: {order_request.quantity}")
    if order_request.price is not None:
        print(f"  Price: {order_request.price}")

    try:
        client = BinanceFuturesClient(
            api_key=api_key,
            api_secret=api_secret,
            base_url=args.base_url,
            timeout=args.timeout,
            recv_window=args.recv_window,
            logger=logger,
        )
        response = client.place_order(params=order_request.to_api_params())
    except BinanceAPIError as exc:
        logger.error(
            "order_failure type=binance_api_error status=%s code=%s message=%s",
            exc.status_code,
            exc.error_code,
            exc,
        )
        print("Order failed.")
        print(f"  Reason: {exc}")
        if exc.status_code is not None:
            print(f"  HTTP Status: {exc.status_code}")
        if exc.error_code is not None:
            print(f"  Binance Error Code: {exc.error_code}")
        return 1
    except NetworkError as exc:
        logger.error("order_failure type=network_error message=%s", exc)
        print("Order failed.")
        print(f"  Reason: {exc}")
        return 1
    except Exception as exc:  # pragma: no cover - defensive catch for CLI UX
        logger.exception("order_failure type=unexpected_error message=%s", exc)
        print("Order failed.")
        print(f"  Unexpected error: {exc}")
        return 1

    order_id = response.get("orderId", "N/A")
    status = response.get("status", "N/A")
    executed_qty = response.get("executedQty", "N/A")
    avg_price = resolve_avg_price(response)

    print("Order Response")
    print(f"  Order ID: {order_id}")
    print(f"  Status: {status}")
    print(f"  Executed Qty: {executed_qty}")
    print(f"  Avg Price: {avg_price}")
    print("Order placed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
