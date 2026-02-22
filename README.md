# signal-trade-engine

Minimal Python project managed with [`uv`](https://docs.astral.sh/uv/).

## Clone the repository

```bash
git clone https://github.com/kamatealif/signal-trade-engine.git
cd signal-trade-engine
```

## Prerequisites

- Python `3.13` (this project uses `.python-version` and `requires-python = ">=3.13"`)
- [`uv`](https://docs.astral.sh/uv/)

Install `uv` (choose one):

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

```bash
# Alternative (if you already use pip)
pip install uv
```

## Set up the project with uv

From the project root:

```bash
uv sync
```

This creates/updates the virtual environment and installs project dependencies.

## Run locally

```bash
uv run python main.py
```

Expected output:

```text
Hello from signal-trade-engine!
```
