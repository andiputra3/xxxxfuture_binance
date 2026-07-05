from __future__ import annotations

from decimal import Decimal
from typing import List

from st_lms.common.enums import LineStatus
from st_lms.models.supertrend_line import SupertrendLine


class LineStatusManager:
    """C004 — Menjaga kontinuitas Supertrend Line.

    Line tidak pernah dihapus, hanya berubah status:
    ACTIVE  → masih relevan dengan harga saat ini
    BROKEN  → harga sudah menembus line
    ARCHIVED → sudah lama broken, tidak relevan lagi
    """

    def evaluate(self, current_price: Decimal, lines: List[SupertrendLine]) -> List[SupertrendLine]:
        """Evaluasi semua line terhadap harga terkini, kembalikan line dgn status terbaru."""
        result: List[SupertrendLine] = []
        for line in lines:
            new_status = self._determine_status(line, current_price)
            result.append(SupertrendLine(
                line_id=line.line_id,
                symbol=line.symbol,
                timeframe=line.timeframe,
                direction=line.direction,
                price=line.price,
                start_timestamp=line.start_timestamp,
                end_timestamp=line.end_timestamp,
                candle_count=line.candle_count,
                touch_count=line.touch_count,
                status=new_status,
            ))
        return result

    def _determine_status(self, line: SupertrendLine, current_price: Decimal) -> LineStatus:
        if line.status == LineStatus.ARCHIVED:
            return LineStatus.ARCHIVED

        broken = self._is_broken(line, current_price)
        if not broken:
            return LineStatus.ACTIVE

        if line.status == LineStatus.BROKEN:
            return LineStatus.ARCHIVED

        return LineStatus.BROKEN

    def _is_broken(self, line: SupertrendLine, current_price: Decimal) -> bool:
        if line.direction.value == "LONG":
            return current_price < line.price
        return current_price > line.price
