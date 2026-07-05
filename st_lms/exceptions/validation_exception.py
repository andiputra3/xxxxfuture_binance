from __future__ import annotations


class ValidationException(Exception):
    """Base exception for validation errors."""


class ModelValidationError(ValidationException):
    """Raised when model validation fails."""


class ConfigValidationError(ValidationException):
    """Raised when configuration validation fails."""


class PlanValidationError(ValidationException):
    """Raised when Trading Plan validation fails."""
