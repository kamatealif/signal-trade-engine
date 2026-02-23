def validate_symbol(symbol):
    if not symbol.isalnum():
        raise ValueError("Invalid symbol")

def validate_side(side):
    if side not in {"BUY", "SELL"}:
        raise ValueError("Side must be BUY or SELL")

def validate_order_type(order_type):
    if order_type not in {"MARKET", "LIMIT"}:
        raise ValueError("Order type must be MARKET or LIMIT")

def validate_quantity(quantity):
    if quantity <= 0:
        raise ValueError("Quantity must be > 0")

def validate_price(price, order_type):
    if order_type == "LIMIT" and (price is None or price <= 0):
        raise ValueError("LIMIT orders require valid price")