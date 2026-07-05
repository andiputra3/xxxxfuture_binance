from __future__ import annotations

from enum import Enum


class Timeframe(str, Enum):
    """Supported Binance Futures timeframes."""

    M1 = "1m"
    M5 = "5m"
    M15 = "15m"
    H1 = "1h"
    H4 = "4h"


class Direction(str, Enum):
    """Market direction."""

    LONG = "LONG"
    SHORT = "SHORT"
    NEUTRAL = "NEUTRAL"


class StructuralState(str, Enum):
    """Official market classification."""

    UPTREND = "UPTREND"
    DOWNTREND = "DOWNTREND"
    SIDEWAY = "SIDEWAY"


class StructuralGeometry(str, Enum):
    """Structural geometry shapes from Understand layer."""

    ASCENDING = "ASCENDING"
    DESCENDING = "DESCENDING"
    CORRIDOR = "CORRIDOR"
    CONVERGING = "CONVERGING"
    DIVERGING = "DIVERGING"
    CHAOTIC = "CHAOTIC"
    SINGLE_DIRECTION = "SINGLE_DIRECTION"
    NO_STRUCTURE = "NO_STRUCTURE"


class PositionSide(str, Enum):
    """Trading position side."""

    LONG = "LONG"
    SHORT = "SHORT"


class PositionState(str, Enum):
    """Position lifecycle."""

    WAITING = "WAITING"
    OPEN = "OPEN"
    PARTIAL = "PARTIAL"
    CLOSING = "CLOSING"
    CLOSED = "CLOSED"


class MACDBucket(str, Enum):
    """MACD classification."""

    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    WEAKENING = "WEAKENING"
    NEUTRAL = "NEUTRAL"


class OpenInterestState(str, Enum):
    """Open Interest classification."""

    INCREASING = "INCREASING"
    DECREASING = "DECREASING"
    FLAT = "FLAT"
    ABSENT = "ABSENT"


class LineStatus(str, Enum):
    """Supertrend Line lifecycle status."""

    ACTIVE = "ACTIVE"
    BROKEN = "BROKEN"
    ARCHIVED = "ARCHIVED"


class WaveState(str, Enum):
    """Supertrend Wave lifecycle."""

    BUILDING = "BUILDING"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    ARCHIVED = "ARCHIVED"


class TradingPlanState(str, Enum):
    """Trading Plan lifecycle."""

    CREATED = "CREATED"
    WAITING = "WAITING"
    READY = "READY"
    AUTHORIZED = "AUTHORIZED"
    EXECUTING = "EXECUTING"
    FINISHED = "FINISHED"
    ARCHIVED = "ARCHIVED"


class GridState(str, Enum):
    """Adaptive Grid lifecycle."""

    WAITING = "WAITING"
    ACTIVE = "ACTIVE"
    SHIFTING = "SHIFTING"
    STOP_NEW_ORDER = "STOP_NEW_ORDER"
    EXITING = "EXITING"
    FINISHED = "FINISHED"


class RiverState(str, Enum):
    """River learning lifecycle."""

    EMPTY = "EMPTY"
    COLLECTING = "COLLECTING"
    LEARNING = "LEARNING"
    STABLE = "STABLE"
    ADAPTIVE = "ADAPTIVE"
    EXPERT = "EXPERT"


class RiverRecommendation(str, Enum):
    """River review output."""

    ALLOW = "ALLOW"
    CAUTION = "CAUTION"
    REJECT = "REJECT"
    UNKNOWN = "UNKNOWN"


class DarwinState(str, Enum):
    """Darwin improvement lifecycle."""

    EMPTY = "EMPTY"
    OBSERVING = "OBSERVING"
    ANALYZING = "ANALYZING"
    IMPROVING = "IMPROVING"
    VALIDATING = "VALIDATING"
    STABLE = "STABLE"


class AuthorizationStatus(str, Enum):
    """Authorization result."""

    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class MarketSession(str, Enum):
    """Market trading session."""

    ASIA = "ASIA"
    LONDON = "LONDON"
    NEW_YORK = "NEW_YORK"
    OVERLAP = "OVERLAP"


class Environment(str, Enum):
    """Runtime environment."""

    SIMULATION = "SIMULATION"
    TESTNET = "TESTNET"
    LIVE = "LIVE"
