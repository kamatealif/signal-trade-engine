"""Order domain logic."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

from bot.errors import ValidationError
from bot.validators import (
    normalize_decimal,
    validate_decimal,
    validate_order_type,
    validate_side,
    validate_symbol,
)


@dataclass(frozen=True)
class OrderRequest:
    symbol: str
    side: str
    order_type: str
    quantity: Decimal
    price: Decimal | None = None

    def to_api_params(self) -> dict[str, str]:
        params: dict[str, str] = {
            "symbol": self.symbol,
            "side": self.side,
            "type": self.order_type,
            "quantity": normalize_decimal(self.quantity),
        }
        if self.order_type == "LIMIT":
            params["timeInForce"] = "GTC"
            if self.price is None:
                raise ValidationError("price is required for LIMIT orders")
            params["price"] = normalize_decimal(self.price)
        return params


def build_order_request(
    *,
    symbol: str,
    side: str,
    order_type: str,
    quantity: str,
    price: str | None,
) -> OrderRequest:
    clean_symbol = validate_symbol(symbol)
    clean_side = validate_side(side)
    clean_order_type = validate_order_type(order_type)
    clean_quantity = validate_decimal("quantity", quantity)

    clean_price: Decimal | None = None
    if clean_order_type == "LIMIT":
        if price is None:
            raise ValidationError("price is required when order type is LIMIT")
        clean_price = validate_decimal("price", price)
    elif price is not None:
        raise ValidationError("price must not be provided for MARKET orders")

    return OrderRequest(
        symbol=clean_symbol,
        side=clean_side,
        order_type=clean_order_type,
        quantity=clean_quantity,
        price=clean_price,
    )


def resolve_avg_price(order_response: dict[str, object]) -> str:
    """Return avg price if available, or derive it from quote/qty."""
    avg_price = str(order_response.get("avgPrice", "")).strip()
    if avg_price and avg_price not in {"0", "0.0", "0.00", "0.00000000"}:
        return avg_price

    executed_qty_raw = str(order_response.get("executedQty", "")).strip()
    quote_raw = str(order_response.get("cumQuote", "")).strip()

    try:
        executed_qty = Decimal(executed_qty_raw)
        cum_quote = Decimal(quote_raw)
    except (InvalidOperation, ValueError):
        return "N/A"

    if executed_qty <= 0:
        return "N/A"
    return normalize_decimal(cum_quote / executed_qty)

