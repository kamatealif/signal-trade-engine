# Binance Futures Testnet Trading Bot

Python CLI app for Binance USDT-M Futures Testnet.  
It supports placing `MARKET` and `LIMIT` orders and includes a continuous price watch mode.

## What This Project Uses

- Python `3.13+`
- `python-binance` for Futures order API calls
- `requests` for watch-mode price polling (`/fapi/v1/ticker/price`)
- `python-dotenv` for loading API credentials from `.env`
- `uv` for dependency and environment management

## Technologies Used

- Python (CLI application)
- Binance Futures Testnet API (USDT-M)
- `python-binance` (order placement/auth wrapper)
- `requests` (price polling in watch mode)
- `python-dotenv` (environment variable loading)
- `argparse` (CLI argument parsing)
- `logging` (file + console logs)
- `uv` (dependency and virtual environment management)

## Local Setup

1. Install dependencies:

```bash
uv sync
```

2. Create `.env` in project root:

```bash
cat > .env <<'EOF'
BINANCE_API_KEY=your_testnet_api_key
BINANCE_API_SECRET=your_testnet_api_secret
EOF
```

## How To Run

Run commands with:

```bash
uv run python main.py ...
```

### MARKET order

```bash
uv run python main.py \
  --symbol BTCUSDT \
  --quantity 0.001 \
  --side BUY \
  --type MARKET
```

### LIMIT order

```bash
uv run python main.py \
  --symbol BTCUSDT \
  --quantity 0.001 \
  --side SELL \
  --type LIMIT \
  --price 120000
```

### Watch mode

```bash
uv run python main.py \
  --symbol BTCUSDT \
  --quantity 0.001 \
  --watch \
  --buy-below 65000 \
  --sell-above 67000
```

Stop watch mode with `Ctrl + C`.

## CLI Arguments

```text
--symbol       required (example: BTCUSDT)
--quantity     required, must be > 0

--side         required in order mode: BUY or SELL
--type         required in order mode: MARKET or LIMIT
--price        required for LIMIT orders

--watch        enable watch mode
--buy-below    required in watch mode
--sell-above   required in watch mode
```

## What Each Project File Does

- `main.py`: app entrypoint, calls CLI runner
- `bot/cli.py`: parses CLI args, routes to order mode or watch mode
- `bot/client.py`: initializes Binance Futures client and sends orders
- `bot/orders.py`: builds order payloads for MARKET/LIMIT
- `bot/validators.py`: validates symbol, side, type, quantity, and price
- `bot/price_watcher.py`: polls latest price and triggers BUY/SELL by thresholds
- `bot/logging_config.py`: sets logging to console and `logs/trading_bot.log`
- `pyproject.toml`: project metadata and dependencies

## Logs

- Log file path: `logs/trading_bot.log`
