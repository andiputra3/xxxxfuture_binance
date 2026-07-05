from __future__ import annotations

from st_lms.common.enums import Timeframe

BOT_NAME = "ST_LMS"
CORE_VERSION = "1.0.0"
DEFAULT_TIMEFRAMES = [Timeframe.M1, Timeframe.M5, Timeframe.M15, Timeframe.H1, Timeframe.H4]
PRIMARY_TIMEFRAME = Timeframe.H4
EXECUTION_TIMEFRAME = Timeframe.M1
