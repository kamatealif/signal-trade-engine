import argparse
import logging

from bot.client import BinanceFuturesClient
from bot.orders import create_order
from bot.price_watcher import watch_price
from bot.validators import *
from bot.logging_config import setup_logging


def main():
    setup_logging()
    logger = logging.getLogger(__name__)

    parser = argparse.ArgumentParser("Binance Futures Trading Bot")

    parser.add_argument("--symbol", required=True)
    parser.add_argument("--quantity", type=float, required=True)

    parser.add_argument("--side", choices=["BUY", "SELL"])
    parser.add_argument("--type", choices=["MARKET", "LIMIT"])
    parser.add_argument("--price", type=float)

    parser.add_argument("--watch", action="store_true")
    parser.add_argument("--buy-below", type=float)
    parser.add_argument("--sell-above", type=float)

    args = parser.parse_args()

    client = BinanceFuturesClient()

    # WATCH MODE
    if args.watch:
        if args.buy_below is None or args.sell_above is None:
            raise ValueError("watch mode requires --buy-below and --sell-above")

        watch_price(
            client=client,
            symbol=args.symbol,
            buy_below=args.buy_below,
            sell_above=args.sell_above,
            quantity=args.quantity,
        )
        return

    # NORMAL ORDER MODE
    validate_symbol(args.symbol)
    validate_side(args.side)
    validate_order_type(args.type)
    validate_quantity(args.quantity)
    validate_price(args.price, args.type)

    response = create_order(
        client,
        args.symbol,
        args.side,
        args.type,
        args.quantity,
        args.price,
    )

    print("\nOrder Placed Successfully")
    print("Order ID:", response.get("orderId"))
    print("Status:", response.get("status"))


if __name__ == "__main__":
    main()