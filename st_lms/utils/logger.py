from __future__ import annotations

import logging

_logger: logging.Logger = logging.getLogger("st_lms")


def get_logger() -> logging.Logger:
    """Get the ST_LMS logger instance."""
    return _logger


def setup_logging(level: int = logging.INFO) -> None:
    """Configure ST_LMS logging."""
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    handler.setFormatter(formatter)
    _logger.addHandler(handler)
    _logger.setLevel(level)
