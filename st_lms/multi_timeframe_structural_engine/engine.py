from __future__ import annotations

from decimal import Decimal
from typing import Dict, List

from st_lms.common.enums import LineStatus, Timeframe, WaveState
from st_lms.config.core_config import PRIMARY_TIMEFRAME
from st_lms.config.supertrend_config import ATR_PERIOD, MIN_LINE_CANDLES, MULTIPLIER
from st_lms.measure.supertrend_calculator import calculate_supertrend_points
from st_lms.models.candle import Candle
from st_lms.models.structure_snapshot import CompressionZone, FibLevel, StructureSnapshot, TrendInfo
from st_lms.models.supertrend_line import SupertrendLine
from st_lms.models.supertrend_point import SupertrendPoint
from st_lms.models.supertrend_wave import SupertrendWave
from st_lms.utils.helpers import generate_line_id, generate_point_id, generate_snapshot_id


class MultiTimeframeStructuralEngine:
    """Orchestrates structure building across all timeframes.

    Output: StructureSnapshot (Trend + Compression + Fibonacci + Points/Lines/Waves)
    """

    def __init__(self) -> None:
        self._symbol: str = ""
        self._points: Dict[Timeframe, List[SupertrendPoint]] = {}
        self._lines: Dict[Timeframe, List[SupertrendLine]] = {}
        self._waves: Dict[Timeframe, List[SupertrendWave]] = {}

    def process(self, symbol: str, candles: dict[Timeframe, List[Candle]]) -> StructureSnapshot:
        """Process all timeframes and return StructureSnapshot."""
        self._symbol = symbol

        for timeframe, tf_candles in candles.items():
            points = self._build_points(symbol, timeframe, tf_candles)
            lines = self._build_lines(symbol, timeframe, points)
            waves = self._build_waves(lines)
            self._points[timeframe] = points
            self._lines[timeframe] = lines
            self._waves[timeframe] = waves

        primary_tf = PRIMARY_TIMEFRAME
        primary_lines = self._lines.get(primary_tf, [])
        trends = self._detect_trends(primary_lines)
        compressions = self._detect_compressions(primary_lines)
        fib_levels = self._calculate_fib_levels(primary_lines, candles.get(primary_tf, []))
        support, resistance = self._find_support_resistance(primary_lines)

        points_dict = {tf.value: pts for tf, pts in self._points.items()}
        lines_dict = {tf.value: ln for tf, ln in self._lines.items()}
        waves_dict = {tf.value: wv for tf, wv in self._waves.items()}
        timestamp = max((p[-1].timestamp for p in self._points.values() if p), default=0)

        return StructureSnapshot(
            snapshot_id=generate_snapshot_id("STRUC"),
            symbol=symbol,
            timestamp=timestamp,
            points=points_dict,
            lines=lines_dict,
            waves=waves_dict,
            trends=trends,
            compressions=compressions,
            fib_levels=fib_levels,
            nearest_support=support,
            nearest_resistance=resistance,
        )

    def _build_points(
        self, symbol: str, timeframe: Timeframe, candles: List[Candle]
    ) -> List[SupertrendPoint]:
        return calculate_supertrend_points(
            symbol, timeframe, candles, period=ATR_PERIOD, multiplier=Decimal(str(MULTIPLIER))
        )

    def _build_lines(
        self, symbol: str, timeframe: Timeframe, points: List[SupertrendPoint]
    ) -> List[SupertrendLine]:
        if not points:
            return []

        lines: List[SupertrendLine] = []
        current_dir = points[0].direction
        segment_start = 0

        for i in range(1, len(points)):
            if points[i].direction != current_dir:
                segment = points[segment_start:i]
                if len(segment) >= MIN_LINE_CANDLES:
                    avg_price = sum(p.price for p in segment) / Decimal(str(len(segment)))
                    touch_count = sum(
                        1 for p in segment
                        if abs(p.price - avg_price) / avg_price < Decimal("0.003")
                    )
                    line = SupertrendLine(
                        line_id=generate_line_id(symbol, str(avg_price)),
                        symbol=symbol,
                        timeframe=timeframe,
                        direction=current_dir,
                        price=avg_price,
                        start_timestamp=segment[0].timestamp,
                        end_timestamp=segment[-1].timestamp,
                        candle_count=len(segment),
                        touch_count=touch_count,
                        status=LineStatus.ACTIVE,
                    )
                    lines.append(line)

                current_dir = points[i].direction
                segment_start = i

        segment = points[segment_start:]
        if len(segment) >= MIN_LINE_CANDLES:
            avg_price = sum(p.price for p in segment) / Decimal(str(len(segment)))
            touch_count = sum(
                1 for p in segment
                if abs(p.price - avg_price) / avg_price < Decimal("0.003")
            )
            line = SupertrendLine(
                line_id=generate_line_id(symbol, str(avg_price)),
                symbol=symbol,
                timeframe=timeframe,
                direction=current_dir,
                price=avg_price,
                start_timestamp=segment[0].timestamp,
                end_timestamp=segment[-1].timestamp,
                candle_count=len(segment),
                touch_count=touch_count,
                status=LineStatus.ACTIVE,
            )
            lines.append(line)

        return lines

    def _build_waves(self, lines: List[SupertrendLine]) -> List[SupertrendWave]:
        if len(lines) < 2:
            return []

        waves: List[SupertrendWave] = []
        for i in range(1, len(lines)):
            prev_line = lines[i - 1]
            curr_line = lines[i]

            if prev_line.direction != curr_line.direction:
                wave = SupertrendWave(
                    wave_id=f"WAV-{prev_line.line_id}-{curr_line.line_id}",
                    symbol=prev_line.symbol,
                    timeframe=prev_line.timeframe,
                    direction=prev_line.direction,
                    start_line_id=prev_line.line_id,
                    end_line_id=curr_line.line_id,
                    amplitude=abs(curr_line.price - prev_line.price),
                    duration=curr_line.end_timestamp - prev_line.start_timestamp,
                    status=WaveState.COMPLETED,
                )
                waves.append(wave)

        return waves

    def _detect_trends(self, lines: List[SupertrendLine]) -> List[TrendInfo]:
        if len(lines) < 2:
            return []

        trends: List[TrendInfo] = []
        current_dir = lines[0].direction.value
        start_idx = 0
        strength = 5

        for i in range(1, len(lines)):
            if lines[i].direction.value != current_dir:
                slope = Decimal("0")
                if i - start_idx > 1:
                    price_range = lines[i - 1].price - lines[start_idx].price
                    slope = price_range / Decimal(str(i - start_idx))

                trends.append(TrendInfo(
                    direction=current_dir,
                    strength=min(strength + (i - start_idx), 10),
                    start_timestamp=lines[start_idx].start_timestamp,
                    end_timestamp=lines[i - 1].end_timestamp,
                    slope=slope,
                ))
                current_dir = lines[i].direction.value
                start_idx = i
                strength = 5

        slope = Decimal("0")
        if len(lines) - start_idx > 1:
            price_range = lines[-1].price - lines[start_idx].price
            slope = price_range / Decimal(str(len(lines) - start_idx))
        trends.append(TrendInfo(
            direction=current_dir,
            strength=min(strength + (len(lines) - start_idx), 10),
            start_timestamp=lines[start_idx].start_timestamp,
            end_timestamp=lines[-1].end_timestamp,
            slope=slope,
        ))

        return trends

    def _detect_compressions(self, lines: List[SupertrendLine]) -> List[CompressionZone]:
        if len(lines) < 3:
            return []

        compressions: List[CompressionZone] = []
        for i in range(2, len(lines)):
            price_range = max(l.price for l in lines[i - 2:i + 1]) - min(l.price for l in lines[i - 2:i + 1])
            avg_price = sum(l.price for l in lines[i - 2:i + 1]) / Decimal("3")
            atr_pct = price_range / avg_price * Decimal("100") if avg_price > Decimal("0") else Decimal("0")

            if atr_pct < Decimal("1.0"):
                compressions.append(CompressionZone(
                    start_timestamp=lines[i - 2].start_timestamp,
                    end_timestamp=lines[i].end_timestamp,
                    upper_price=max(l.price for l in lines[i - 2:i + 1]),
                    lower_price=min(l.price for l in lines[i - 2:i + 1]),
                    atr_percent=atr_pct,
                ))

        return compressions

    def _calculate_fib_levels(self, lines: List[SupertrendLine], candles: List[Candle]) -> List[FibLevel]:
        if len(lines) < 2:
            return []

        high_price = max(l.price for l in lines)
        low_price = min(l.price for l in lines)
        diff = high_price - low_price
        ratios = [Decimal("0"), Decimal("0.236"), Decimal("0.382"), Decimal("0.5"), Decimal("0.618"), Decimal("0.786"), Decimal("1.0")]

        return [FibLevel(level=r, price=high_price - diff * r) for r in ratios]

    def _find_support_resistance(self, lines: List[SupertrendLine]) -> tuple[Decimal, Decimal]:
        if not lines:
            return Decimal("1"), Decimal("2")
        prices = [l.price for l in lines if l.price > Decimal("0")]
        if not prices:
            return Decimal("1"), Decimal("2")
        lo, hi = min(prices), max(prices)
        # Guarantee support <= resistance regardless of market direction
        return (lo, hi) if lo <= hi else (hi, lo)
