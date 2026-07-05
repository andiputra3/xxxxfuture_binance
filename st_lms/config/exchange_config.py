from __future__ import annotations

import os

from st_lms.common.core_constants import BINANCE_FUTURES
from st_lms.common.enums import Environment

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

EXCHANGE = BINANCE_FUTURES
ENVIRONMENT = Environment(os.getenv("ST_LMS_ENV", "SIMULATION"))
API_KEY = os.getenv("BINANCE_API_KEY", "")
API_SECRET = os.getenv("BINANCE_API_SECRET", "")
TESTNET_API_KEY = os.getenv("BINANCE_TESTNET_API_KEY", "")
TESTNET_API_SECRET = os.getenv("BINANCE_TESTNET_API_SECRET", "")
