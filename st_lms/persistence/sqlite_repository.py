"""SQLite Repository Implementation.

Production-ready SQLite repositories for ST_LMS.
Provides durable storage with proper schema management.
"""

import json
import sqlite3
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, List, Optional

from st_lms.models.trading_plan import TradingPlan
from st_lms.models.learning_snapshot import TradeOutcome
from st_lms.models.structure_snapshot import StructureSnapshot
from st_lms.persistence.base_repository import BaseRepository


class SqliteConnectionManager:
    """Manage SQLite connections with proper lifecycle."""

    def __init__(self, db_path: str = "st_lms.db"):
        self.db_path = db_path
        self._connection: Optional[sqlite3.Connection] = None

    def get_connection(self) -> sqlite3.Connection:
        if self._connection is None:
            self._connection = sqlite3.connect(self.db_path)
            self._connection.row_factory = sqlite3.Row
            # Enable foreign keys
            self._connection.execute("PRAGMA foreign_keys = ON")
        return self._connection

    def close(self) -> None:
        if self._connection:
            self._connection.close()
            self._connection = None


# Global connection manager (singleton pattern for simplicity)
_db_manager: Optional[SqliteConnectionManager] = None


def get_db_manager(db_path: str = "st_lms.db") -> SqliteConnectionManager:
    global _db_manager
    if _db_manager is None or _db_manager.db_path != db_path:
        _db_manager = SqliteConnectionManager(db_path)
    return _db_manager


def init_database(db_path: str = "st_lms.db") -> None:
    """Initialize database schema."""
    conn = get_db_manager(db_path).get_connection()
    cursor = conn.cursor()

    # Trading Plans table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trading_plans (
            plan_id TEXT PRIMARY KEY,
            symbol TEXT NOT NULL,
            direction TEXT NOT NULL,
            status TEXT NOT NULL,
            confidence REAL NOT NULL,
            entry_price REAL,
            stop_loss REAL,
            take_profit REAL,
            position_size REAL,
            created_at TEXT NOT NULL,
            updated_at TEXT,
            executed_at TEXT,
            closed_at TEXT,
            pnl REAL,
            metadata TEXT
        )
    """)

    # Trade Outcomes table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trade_outcomes (
            trade_id TEXT PRIMARY KEY,
            plan_id TEXT NOT NULL,
            symbol TEXT NOT NULL,
            direction TEXT NOT NULL,
            entry_price REAL NOT NULL,
            exit_price REAL NOT NULL,
            pnl REAL NOT NULL,
            pnl_percent REAL NOT NULL,
            exit_reason TEXT NOT NULL,
            duration_seconds INTEGER,
            created_at TEXT NOT NULL,
            metadata TEXT,
            FOREIGN KEY (plan_id) REFERENCES trading_plans(plan_id)
        )
    """)

    # Historical Structures table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS historical_structures (
            snapshot_id TEXT PRIMARY KEY,
            symbol TEXT NOT NULL,
            timeframe TEXT NOT NULL,
            structure_type TEXT NOT NULL,
            price_level REAL NOT NULL,
            strength INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            metadata TEXT
        )
    """)

    # Learning Data table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS learning_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            key TEXT NOT NULL,
            value TEXT NOT NULL,
            confidence REAL,
            created_at TEXT NOT NULL,
            UNIQUE(category, key)
        )
    """)

    # Backtest Results table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS backtest_results (
            backtest_id TEXT PRIMARY KEY,
            strategy_name TEXT NOT NULL,
            symbol TEXT NOT NULL,
            timeframe TEXT NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            total_trades INTEGER NOT NULL,
            win_rate REAL NOT NULL,
            total_pnl REAL NOT NULL,
            max_drawdown REAL NOT NULL,
            sharpe_ratio REAL,
            created_at TEXT NOT NULL,
            metrics TEXT
        )
    """)

    # Create indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_plans_status ON trading_plans(status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_plans_symbol ON trading_plans(symbol)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_outcomes_plan_id ON trade_outcomes(plan_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_structures_symbol ON historical_structures(symbol)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_learning_category ON learning_data(category)")

    conn.commit()


class SqlitePlanRepository(BaseRepository):
    """SQLite repository for Trading Plans."""

    def __init__(self, db_path: str = "st_lms.db"):
        self.db_path = db_path
        init_database(db_path)

    def _get_conn(self) -> sqlite3.Connection:
        return get_db_manager(self.db_path).get_connection()

    def save(self, plan: TradingPlan) -> None:
        conn = self._get_conn()
        cursor = conn.cursor()

        metadata_json = json.dumps(plan.to_dict()) if hasattr(plan, 'to_dict') else json.dumps({})

        cursor.execute("""
            INSERT OR REPLACE INTO trading_plans 
            (plan_id, symbol, direction, status, confidence, entry_price, stop_loss, take_profit,
             position_size, created_at, updated_at, executed_at, closed_at, pnl, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            plan.plan_id,
            plan.symbol,
            plan.direction.value if hasattr(plan.direction, 'value') else plan.direction,
            plan.status.value if hasattr(plan.status, 'value') else plan.status,
            float(plan.confidence),
            float(plan.entry_price) if plan.entry_price else None,
            float(plan.stop_loss) if plan.stop_loss else None,
            float(plan.take_profit) if plan.take_profit else None,
            float(plan.position_size) if plan.position_size else None,
            plan.created_at.isoformat(),
            plan.updated_at.isoformat() if plan.updated_at else None,
            plan.executed_at.isoformat() if plan.executed_at else None,
            plan.closed_at.isoformat() if plan.closed_at else None,
            float(plan.pnl) if plan.pnl else None,
            metadata_json
        ))

        conn.commit()

    def get(self, plan_id: str) -> Optional[TradingPlan]:
        # For now, return None - full deserialization requires complete model
        # This is a placeholder for future implementation
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM trading_plans WHERE plan_id = ?", (plan_id,))
        row = cursor.fetchone()
        if row:
            return self._row_to_plan(row)
        return None

    def _row_to_plan(self, row: sqlite3.Row) -> Optional[TradingPlan]:
        """Convert database row to TradingPlan object."""
        try:
            from st_lms.enums.trading_enums import Direction, PlanStatus
            from decimal import Decimal
            from datetime import datetime

            return TradingPlan(
                plan_id=row["plan_id"],
                symbol=row["symbol"],
                direction=Direction(row["direction"]),
                status=PlanStatus(row["status"]),
                confidence=Decimal(str(row["confidence"])),
                entry_price=Decimal(str(row["entry_price"])) if row["entry_price"] else None,
                stop_loss=Decimal(str(row["stop_loss"])) if row["stop_loss"] else None,
                take_profit=Decimal(str(row["take_profit"])) if row["take_profit"] else None,
                position_size=Decimal(str(row["position_size"])) if row["position_size"] else None,
                created_at=datetime.fromisoformat(row["created_at"]),
                updated_at=datetime.fromisoformat(row["updated_at"]) if row["updated_at"] else None,
                executed_at=datetime.fromisoformat(row["executed_at"]) if row["executed_at"] else None,
                closed_at=datetime.fromisoformat(row["closed_at"]) if row["closed_at"] else None,
                pnl=Decimal(str(row["pnl"])) if row["pnl"] else None,
            )
        except Exception:
            return None

    def list_all(self) -> List[TradingPlan]:
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM trading_plans ORDER BY created_at DESC")
        rows = cursor.fetchall()
        plans = []
        for row in rows:
            plan = self._row_to_plan(row)
            if plan:
                plans.append(plan)
        return plans

    def delete(self, plan_id: str) -> bool:
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM trading_plans WHERE plan_id = ?", (plan_id,))
        conn.commit()
        return cursor.rowcount > 0

    def count(self) -> int:
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM trading_plans")
        return cursor.fetchone()[0]

    def find_by_status(self, status: str) -> List[TradingPlan]:
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM trading_plans WHERE status = ?", (status,))
        rows = cursor.fetchall()
        plans = []
        for row in rows:
            plan = self._row_to_plan(row)
            if plan:
                plans.append(plan)
        return plans

    def find_by_symbol(self, symbol: str) -> List[TradingPlan]:
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM trading_plans WHERE symbol = ?", (symbol,))
        rows = cursor.fetchall()
        plans = []
        for row in rows:
            plan = self._row_to_plan(row)
            if plan:
                plans.append(plan)
        return plans


class SqliteOutcomeRepository(BaseRepository):
    """SQLite repository for Trade Outcomes."""

    def __init__(self, db_path: str = "st_lms.db"):
        self.db_path = db_path
        init_database(db_path)

    def _get_conn(self) -> sqlite3.Connection:
        return get_db_manager(self.db_path).get_connection()

    def save(self, outcome: TradeOutcome) -> None:
        conn = self._get_conn()
        cursor = conn.cursor()

        metadata_json = json.dumps(outcome.to_dict()) if hasattr(outcome, 'to_dict') else json.dumps({})

        cursor.execute("""
            INSERT OR REPLACE INTO trade_outcomes
            (trade_id, plan_id, symbol, direction, entry_price, exit_price, pnl, pnl_percent,
             exit_reason, duration_seconds, created_at, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            outcome.trade_id,
            outcome.plan_id,
            outcome.symbol,
            outcome.direction.value if hasattr(outcome.direction, 'value') else outcome.direction,
            float(outcome.entry_price),
            float(outcome.exit_price),
            float(outcome.pnl),
            float(outcome.pnl_percent),
            outcome.exit_reason.value if hasattr(outcome.exit_reason, 'value') else outcome.exit_reason,
            outcome.duration_seconds,
            outcome.created_at.isoformat(),
            metadata_json
        ))

        conn.commit()

    def get(self, trade_id: str) -> Optional[TradeOutcome]:
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM trade_outcomes WHERE trade_id = ?", (trade_id,))
        row = cursor.fetchone()
        if row:
            return self._row_to_outcome(row)
        return None

    def _row_to_outcome(self, row: sqlite3.Row) -> Optional[TradeOutcome]:
        """Convert database row to TradeOutcome object."""
        try:
            from st_lms.enums.trading_enums import Direction, ExitReason
            from decimal import Decimal
            from datetime import datetime

            return TradeOutcome(
                trade_id=row["trade_id"],
                plan_id=row["plan_id"],
                symbol=row["symbol"],
                direction=Direction(row["direction"]),
                entry_price=Decimal(str(row["entry_price"])),
                exit_price=Decimal(str(row["exit_price"])),
                pnl=Decimal(str(row["pnl"])),
                pnl_percent=Decimal(str(row["pnl_percent"])),
                exit_reason=ExitReason(row["exit_reason"]),
                duration_seconds=row["duration_seconds"],
                created_at=datetime.fromisoformat(row["created_at"]),
            )
        except Exception:
            return None

    def list_all(self) -> List[TradeOutcome]:
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM trade_outcomes ORDER BY created_at DESC")
        rows = cursor.fetchall()
        outcomes = []
        for row in rows:
            outcome = self._row_to_outcome(row)
            if outcome:
                outcomes.append(outcome)
        return outcomes

    def delete(self, trade_id: str) -> bool:
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM trade_outcomes WHERE trade_id = ?", (trade_id,))
        conn.commit()
        return cursor.rowcount > 0

    def count(self) -> int:
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM trade_outcomes")
        return cursor.fetchone()[0]

    def find_by_plan_id(self, plan_id: str) -> List[TradeOutcome]:
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM trade_outcomes WHERE plan_id = ?", (plan_id,))
        rows = cursor.fetchall()
        outcomes = []
        for row in rows:
            outcome = self._row_to_outcome(row)
            if outcome:
                outcomes.append(outcome)
        return outcomes

    def get_win_rate(self) -> float:
        """Calculate overall win rate."""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM trade_outcomes WHERE pnl > 0")
        wins = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM trade_outcomes")
        total = cursor.fetchone()[0]
        return wins / total if total > 0 else 0.0


class SqliteStructureRepository(BaseRepository):
    """SQLite repository for Historical Structures."""

    def __init__(self, db_path: str = "st_lms.db"):
        self.db_path = db_path
        init_database(db_path)

    def _get_conn(self) -> sqlite3.Connection:
        return get_db_manager(self.db_path).get_connection()

    def save(self, snapshot: StructureSnapshot) -> None:
        conn = self._get_conn()
        cursor = conn.cursor()

        metadata_json = json.dumps(snapshot.to_dict()) if hasattr(snapshot, 'to_dict') else json.dumps({})

        cursor.execute("""
            INSERT OR REPLACE INTO historical_structures
            (snapshot_id, symbol, timeframe, structure_type, price_level, strength, created_at, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            snapshot.snapshot_id,
            snapshot.symbol,
            snapshot.timeframe,
            snapshot.structure_type.value if hasattr(snapshot.structure_type, 'value') else snapshot.structure_type,
            float(snapshot.price_level),
            snapshot.strength,
            snapshot.created_at.isoformat(),
            metadata_json
        ))

        conn.commit()

    def get(self, snapshot_id: str) -> Optional[StructureSnapshot]:
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM historical_structures WHERE snapshot_id = ?", (snapshot_id,))
        row = cursor.fetchone()
        if row:
            return self._row_to_snapshot(row)
        return None

    def _row_to_snapshot(self, row: sqlite3.Row) -> Optional[StructureSnapshot]:
        """Convert database row to StructureSnapshot object."""
        try:
            from st_lms.enums.market_enums import StructureType
            from decimal import Decimal
            from datetime import datetime

            return StructureSnapshot(
                snapshot_id=row["snapshot_id"],
                symbol=row["symbol"],
                timeframe=row["timeframe"],
                structure_type=StructureType(row["structure_type"]),
                price_level=Decimal(str(row["price_level"])),
                strength=row["strength"],
                created_at=datetime.fromisoformat(row["created_at"]),
            )
        except Exception:
            return None

    def list_all(self) -> List[StructureSnapshot]:
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM historical_structures ORDER BY created_at DESC")
        rows = cursor.fetchall()
        snapshots = []
        for row in rows:
            snapshot = self._row_to_snapshot(row)
            if snapshot:
                snapshots.append(snapshot)
        return snapshots

    def delete(self, snapshot_id: str) -> bool:
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM historical_structures WHERE snapshot_id = ?", (snapshot_id,))
        conn.commit()
        return cursor.rowcount > 0

    def count(self) -> int:
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM historical_structures")
        return cursor.fetchone()[0]

    def find_by_symbol(self, symbol: str) -> List[StructureSnapshot]:
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM historical_structures WHERE symbol = ?", (symbol,))
        rows = cursor.fetchall()
        snapshots = []
        for row in rows:
            snapshot = self._row_to_snapshot(row)
            if snapshot:
                snapshots.append(snapshot)
        return snapshots


class SqliteLearningRepository:
    """SQLite repository for Learning Data."""

    def __init__(self, db_path: str = "st_lms.db"):
        self.db_path = db_path
        init_database(db_path)

    def _get_conn(self) -> sqlite3.Connection:
        return get_db_manager(self.db_path).get_connection()

    def store(self, category: str, key: str, value: Any, confidence: Optional[float] = None) -> None:
        conn = self._get_conn()
        cursor = conn.cursor()

        value_json = json.dumps(value) if not isinstance(value, str) else value

        cursor.execute("""
            INSERT OR REPLACE INTO learning_data (category, key, value, confidence, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            category,
            key,
            value_json,
            confidence,
            datetime.utcnow().isoformat()
        ))

        conn.commit()

    def get(self, category: str, key: str) -> Optional[Any]:
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM learning_data WHERE category = ? AND key = ?", (category, key))
        row = cursor.fetchone()
        if row:
            try:
                return json.loads(row["value"])
            except json.JSONDecodeError:
                return row["value"]
        return None

    def delete(self, category: str, key: str) -> bool:
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM learning_data WHERE category = ? AND key = ?", (category, key))
        conn.commit()
        return cursor.rowcount > 0

    def count(self) -> int:
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM learning_data")
        return cursor.fetchone()[0]

    def find_by_category(self, category: str) -> Dict[str, Any]:
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT key, value FROM learning_data WHERE category = ?", (category,))
        rows = cursor.fetchall()
        result = {}
        for row in rows:
            try:
                result[row["key"]] = json.loads(row["value"])
            except json.JSONDecodeError:
                result[row["key"]] = row["value"]
        return result


class SqliteBacktestRepository:
    """SQLite repository for Backtest Results."""

    def __init__(self, db_path: str = "st_lms.db"):
        self.db_path = db_path
        init_database(db_path)

    def _get_conn(self) -> sqlite3.Connection:
        return get_db_manager(self.db_path).get_connection()

    def save(self, backtest_result: Dict[str, Any]) -> None:
        conn = self._get_conn()
        cursor = conn.cursor()

        metrics_json = json.dumps(backtest_result.get('metrics', {}))

        cursor.execute("""
            INSERT OR REPLACE INTO backtest_results
            (backtest_id, strategy_name, symbol, timeframe, start_date, end_date,
             total_trades, win_rate, total_pnl, max_drawdown, sharpe_ratio, created_at, metrics)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            backtest_result['backtest_id'],
            backtest_result['strategy_name'],
            backtest_result['symbol'],
            backtest_result['timeframe'],
            backtest_result['start_date'],
            backtest_result['end_date'],
            backtest_result['total_trades'],
            backtest_result['win_rate'],
            backtest_result['total_pnl'],
            backtest_result['max_drawdown'],
            backtest_result.get('sharpe_ratio'),
            datetime.utcnow().isoformat(),
            metrics_json
        ))

        conn.commit()

    def get(self, backtest_id: str) -> Optional[Dict[str, Any]]:
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM backtest_results WHERE backtest_id = ?", (backtest_id,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None

    def list_all(self) -> List[Dict[str, Any]]:
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM backtest_results ORDER BY created_at DESC")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def delete(self, backtest_id: str) -> bool:
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM backtest_results WHERE backtest_id = ?", (backtest_id,))
        conn.commit()
        return cursor.rowcount > 0

    def count(self) -> int:
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM backtest_results")
        return cursor.fetchone()[0]

    def find_best_strategy(self) -> Optional[Dict[str, Any]]:
        """Find the best performing strategy by total PnL."""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM backtest_results 
            ORDER BY total_pnl DESC 
            LIMIT 1
        """)
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None
