import time
import logging
import requests

logger = logging.getLogger(__name__)

BASE_URL = "https://testnet.binancefuture.com"


def fetch_price(symbol: str) -> float:
    url = f"{BASE_URL}/fapi/v1/ticker/price"
    resp = requests.get(url, params={"symbol": symbol}, timeout=5)

    resp.raise_for_status()
    data = resp.json()

    if "price" not in data:
        raise RuntimeError(f"Invalid price response: {data}")

    return float(data["price"])


def watch_price(
    client,
    symbol,
    buy_below,
    sell_above,
    quantity,
    poll_interval=3,
):
    last_price = None
    position = None  # None or "LONG"

    logger.info(f"Started price watcher for {symbol}")

    while True:
        try:
            price = fetch_price(symbol)

            if last_price is None:
                movement = "→ START"
            elif price > last_price:
                movement = "⬆ UP"
            elif price < last_price:
                movement = "⬇ DOWN"
            else:
                movement = "→ FLAT"

            print(
                f"Price: {price:.2f} | {movement} | "
                f"BUY < {buy_below} | SELL > {sell_above}"
            )

            logger.info(
                f"price={price}, movement={movement}, position={position}"
            )

            # BUY
            if price <= buy_below and position is None:
                logger.info("BUY condition met")
                client.place_order(
                    symbol=symbol,
                    side="BUY",
                    type="MARKET",
                    quantity=quantity,
                )
                position = "LONG"
                logger.info("BUY executed")

            # SELL
            elif price >= sell_above and position == "LONG":
                logger.info("SELL condition met")
                client.place_order(
                    symbol=symbol,
                    side="SELL",
                    type="MARKET",
                    quantity=quantity,
                )
                position = None
                logger.info("SELL executed")

            last_price = price
            time.sleep(poll_interval)

        except KeyboardInterrupt:
            print("\n🛑 Bot stopped by user")
            logger.info("Bot stopped by user")
            break

        except Exception as e:
            logger.error(f"Price fetch failed: {e}")
            time.sleep(poll_interval)