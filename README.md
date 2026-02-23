# Binance Futures Testnet Trading Bot (Assignment)

Python CLI app to place `MARKET` and `LIMIT` orders on Binance Futures Testnet (USDT-M), with input validation, structured modules, logging, and error handling.
The API layer uses the `python-binance` package.

## Features

- Place orders on Binance Futures Testnet (`https://testnet.binancefuture.com`)
- Supports both sides: `BUY`, `SELL`
- Supports order types: `MARKET`, `LIMIT`
- Validates CLI inputs (`symbol`, `side`, `order type`, `quantity`, `price`)
- Logs API requests/responses/errors to file
- Clear CLI output: request summary + response details + success/failure

## Project Structure

```text
.
├── bot/
│   ├── cli.py              # CLI layer
│   ├── client.py           # Binance API client wrapper
│   ├── errors.py           # custom exceptions
│   ├── logging_config.py   # file logging setup
│   ├── orders.py           # order request model and logic
│   └── validators.py       # input validation helpers
├── logs/                   # log files are generated here
└── main.py                 # app entrypoint
```

## Prerequisites

- Python `3.13+`
- Binance Futures Testnet account + API credentials

## Setup

```bash
uv sync
```

Set credentials:

```bash
cat > .env <<'EOF'
API_KEY=your_testnet_api_key
SECRET_KEY=your_testnet_api_secret
EOF
```

## Usage

### MARKET order example

```bash
uv run python main.py \
  --symbol BTCUSDT \
  --side BUY \
  --order-type MARKET \
  --quantity 0.001
```

### LIMIT order example

```bash
uv run python main.py \
  --symbol BTCUSDT \
  --side SELL \
  --order-type LIMIT \
  --quantity 0.001 \
  --price 120000
```

## CLI Options

```text
--symbol       required, e.g. BTCUSDT
--side         required, BUY or SELL
--order-type   required, MARKET or LIMIT
--quantity     required, > 0
--price        required only for LIMIT
--api-key      optional (fallback: API_KEY from .env)
--api-secret   optional (fallback: SECRET_KEY from .env)
--base-url     optional (default: https://testnet.binancefuture.com)
--log-file     optional (default: logs/trading_bot.log)
--timeout      optional (default: 15 seconds)
--recv-window  optional (default: 5000 ms)
```

## Output

The program prints:

- Order request summary
- Order response details:
  - `orderId`
  - `status`
  - `executedQty`
  - `avgPrice` (or derived when possible)
- Final success/failure message

## Logs

Logs are written to:

```text
logs/trading_bot.log
```

Logged events include:

- API request metadata
- API response payloads
- Validation/API/network errors

To generate separate deliverable logs:

```bash
# Market log
uv run python main.py ... --order-type MARKET --log-file logs/market_order.log

# Limit log
uv run python main.py ... --order-type LIMIT --price 120000 --log-file logs/limit_order.log
```

## Assumptions

- This bot targets Binance USDT-M Futures Testnet only.
- Quantity/price precision and symbol filters are ultimately enforced by Binance.
- For `LIMIT` orders, `timeInForce=GTC` is used.
