from __future__ import annotations


class TradingException(Exception):
    """Base exception for trading layer errors."""


class AuthorizationError(TradingException):
    """Raised when authorization fails."""


class ExecutionError(TradingException):
    """Raised when order execution fails."""


class RiskLimitExceeded(TradingException):
    """Raised when risk limit is exceeded."""
