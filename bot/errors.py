"""Custom exceptions used by the trading bot."""


class BotError(Exception):
    """Base exception for all bot-related errors."""


class ValidationError(BotError):
    """Raised when CLI input does not pass validation."""


class APIError(BotError):
    """Base exception for API communication errors."""


class NetworkError(APIError):
    """Raised when network communication fails."""


class BinanceAPIError(APIError):
    """Raised when Binance returns a non-success response."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        error_code: int | None = None,
    ) -> None:
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(message)

