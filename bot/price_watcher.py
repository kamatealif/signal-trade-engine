import time
import logging

logger = logging.getLogger(__name__)

def watch_price(
    client,
    symbol,
    buy_below,
    sell_above,
    quantity,
    poll_interval=3
):
    last_price = None
    position = None  # None or "LONG"

    logger.info(f"Started price watcher for {symbol}")

    while True:
        try:
            ticker = client.client.futures_symbol_ticker(symbol=symbol)
            price = float(ticker["price"])

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

            # BUY LOGIC
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

            # SELL LOGIC
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
            logger.exception("Error in price watcher loop")
            time.sleep(poll_interval)