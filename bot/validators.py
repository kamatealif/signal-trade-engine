"""Input validation helpers for CLI arguments."""

from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation

from bot.errors import ValidationError

VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT"}
SYMBOL_PATTERN = re.compile(r"^[A-Z0-9]{5,20}$")


def validate_symbol(value: str) -> str:
    symbol = value.strip().upper()
    if not symbol:
        raise ValidationError("symbol is required")
    if not SYMBOL_PATTERN.fullmatch(symbol):
        raise ValidationError(
            "symbol must be uppercase alphanumeric and between 5-20 characters"
        )
    return symbol


def validate_side(value: str) -> str:
    side = value.strip().upper()
    if side not in VALID_SIDES:
        raise ValidationError("side must be BUY or SELL")
    return side


def validate_order_type(value: str) -> str:
    order_type = value.strip().upper()
    if order_type not in VALID_ORDER_TYPES:
        raise ValidationError("order type must be MARKET or LIMIT")
    return order_type


def validate_decimal(field_name: str, value: str) -> Decimal:
    try:
        number = Decimal(value)
    except (InvalidOperation, ValueError) as exc:
        raise ValidationError(f"{field_name} must be a valid decimal number") from exc

    if number <= 0:
        raise ValidationError(f"{field_name} must be greater than 0")
    return number


def normalize_decimal(value: Decimal) -> str:
    text = format(value, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text

