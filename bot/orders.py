from binance.enums import ORDER_TYPE_MARKET, ORDER_TYPE_LIMIT, TIME_IN_FORCE_GTC

def create_order(client, symbol, side, order_type, quantity, price=None):
    order = {
        "symbol": symbol,
        "side": side,
        "quantity": quantity,
    }

    if order_type == "MARKET":
        order["type"] = ORDER_TYPE_MARKET

    elif order_type == "LIMIT":
        order["type"] = ORDER_TYPE_LIMIT
        order["price"] = price
        order["timeInForce"] = TIME_IN_FORCE_GTC

    return client.place_order(**order)