# Binance Futures Testnet Trading Bot

A Python CLI bot for Binance USDT-M Futures **Testnet**.  
It can:

- Place one-off `MARKET` and `LIMIT` orders
- Run a continuous watch loop that auto-buys below a threshold and auto-sells above a threshold
- Log all trading actions to both console and file

## Overview

This project is intentionally lightweight and CLI-first:

- `argparse` handles command input
- `python-binance` sends authenticated Futures orders
- `requests` fetches latest price in watch mode
- `python-dotenv` loads credentials from `.env`
- `uv` manages dependencies and execution

The bot targets Binance Futures Testnet endpoint:

- API base URL for orders: `https://testnet.binancefuture.com`
- Price polling endpoint: `/fapi/v1/ticker/price`

## Features

- Direct order execution for `MARKET` and `LIMIT` orders
- `LIMIT` order placement with `GTC` time-in-force
- Watch mode strategy loop that polls price every 3 seconds
- Local position tracking with two states: `None` and `LONG`
- Auto-buy trigger when `price <= buy_below` and no local position is open
- Auto-sell trigger when `price >= sell_above` and local position is `LONG`
- Operational logging to console and `logs/trading_bot.log`

## Repository Layout

- `main.py` - App entrypoint
- `bot/cli.py` - Argument parsing and mode routing
- `bot/client.py` - Binance client initialization and order submission
- `bot/orders.py` - Order payload creation (`MARKET` / `LIMIT`)
- `bot/validators.py` - Input validation
- `bot/price_watcher.py` - Price polling loop and threshold logic
- `bot/logging_config.py` - Console/file logger setup
- `pyproject.toml` - Project metadata, dependencies, and CLI script

## Requirements

- Python `3.13+`
- Binance Futures Testnet API key and secret
- `uv` installed locally

## Setup

1. Install dependencies:

```bash
uv sync
```

2. Create `.env` in the project root:

```bash
cat > .env <<'EOF'
BINANCE_API_KEY=your_testnet_api_key
BINANCE_API_SECRET=your_testnet_api_secret
EOF
```

3. (Optional) Verify CLI entrypoint:

```bash
uv run trading-bot --help
```

## Running the Bot

You can run either of these forms:

- `uv run trading-bot ...`
- `uv run python main.py ...`

### 1. Place a MARKET Order

```bash
uv run trading-bot \
  --symbol BTCUSDT \
  --quantity 0.001 \
  --side BUY \
  --type MARKET
```

### 2. Place a LIMIT Order

```bash
uv run trading-bot \
  --symbol BTCUSDT \
  --quantity 0.001 \
  --side SELL \
  --type LIMIT \
  --price 120000
```

### 3. Start Watch Mode

```bash
uv run trading-bot \
  --symbol BTCUSDT \
  --quantity 0.001 \
  --watch \
  --buy-below 65000 \
  --sell-above 67000
```

Stop the loop with `Ctrl + C`.

## CLI Argument Reference

### Required in all modes

- `--symbol` (example: `BTCUSDT`)
- `--quantity` (must be `> 0`)

### Required in direct order mode

- `--side`: `BUY` or `SELL`
- `--type`: `MARKET` or `LIMIT`
- `--price`: required only when `--type LIMIT`

### Required in watch mode

- `--watch`
- `--buy-below`
- `--sell-above`

## Validation and Error Behavior

Input validation currently enforces:

- `symbol` must be alphanumeric
- `side` must be `BUY` or `SELL`
- `type` must be `MARKET` or `LIMIT`
- `quantity` must be positive
- `LIMIT` orders must include positive `price`

Common runtime failures:

- Missing credentials: `RuntimeError("Missing Binance API credentials")`
- Network/API errors during watch loop are logged as `Price fetch failed: ...` and retried

## Logging

- Logs are written to console (`StreamHandler`) and `logs/trading_bot.log` (`FileHandler`)
- Log format:

```text
timestamp | LEVEL | message
```

Watch mode logs include:

- Current polled price and movement
- Position state transitions
- Buy/sell trigger events
- Full order payload and exchange response

## Important Notes and Limitations

- This bot is configured for **Testnet** only.
- Watch mode keeps position state in memory only.
- If the process restarts, local position state resets.
- No reconciliation is performed against existing exchange positions on startup.
- Symbol precision/step-size filters are not enforced yet.
- No stop-loss, take-profit, leverage controls, or risk caps are built in.

## Quick Troubleshooting

- `Missing Binance API credentials`: confirm `.env` exists in project root and names match exactly.
- `Invalid symbol` or argument errors: verify CLI flags and values match the reference above.
- Orders rejected by Binance: verify symbol exists on Futures Testnet and quantity/price meet exchange rules.
