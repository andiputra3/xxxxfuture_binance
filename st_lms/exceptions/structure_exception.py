from __future__ import annotations


class StructureException(Exception):
    """Base exception for structure layer errors."""


class LineBuildError(StructureException):
    """Raised when Supertrend Line construction fails."""


class WaveBuildError(StructureException):
    """Raised when Wave construction fails."""


class FusionError(StructureException):
    """Raised when structure fusion across timeframes fails."""
