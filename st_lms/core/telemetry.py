"""
ST_LMS Telemetry Module
Merekam setiap langkah pipeline secara real-time untuk Dashboard Monitoring.
Thread-safe dan berkapasitas buffer terbatas (Circular Buffer).
"""
import threading
import time
from collections import deque
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional
from enum import Enum
import json

class PipelineStage(Enum):
    OBSERVE = "C001 - Observe"
    MEASURE = "C002 - Measure"
    STRUCTURE = "C003 - Multi-TF Structure"
    PRESERVE = "C004 - Preserve"
    REMEMBER = "C005 - Remember"
    SELECT = "C006 - Select"
    UNDERSTAND = "C007 - Understand"
    CLASSIFY = "C008 - Classify"
    PLAN = "C009 - Trading Plan"
    RIVER_REVIEW = "C010 - River Review"
    AUTHORIZE = "C011 - Authorize"
    EXECUTE = "C012 - Execute"
    POST_TRADE = "Post-Trade Learning"

@dataclass
class TelemetryEvent:
    timestamp: float
    stage: str
    action: str
    details: Dict[str, Any]
    status: str  # SUCCESS, WARNING, ERROR, REJECTED
    duration_ms: Optional[float] = None

    def to_dict(self):
        return {
            "timestamp": self.timestamp,
            "stage": self.stage,
            "action": self.action,
            "details": self.details,
            "status": self.status,
            "duration_ms": self.duration_ms
        }

class TelemetrySystem:
    def __init__(self, max_events: int = 500):
        self.events = deque(maxlen=max_events)
        self.lock = threading.Lock()
        self.current_cycle_id = 0
        self.pipeline_logs = {}  # Log per cycle
        
    def start_cycle(self):
        with self.lock:
            self.current_cycle_id = int(time.time() * 1000)
            self.pipeline_logs[self.current_cycle_id] = []
            
    def log(self, stage: PipelineStage, action: str, details: Dict[str, Any], 
            status: str = "SUCCESS", duration_ms: Optional[float] = None):
        event = TelemetryEvent(
            timestamp=time.time(),
            stage=stage.value,
            action=action,
            details=details,
            status=status,
            duration_ms=duration_ms
        )
        
        with self.lock:
            self.events.append(event)
            if self.current_cycle_id in self.pipeline_logs:
                self.pipeline_logs[self.current_cycle_id].append(event.to_dict())
                
    def get_recent_events(self, limit: int = 50) -> List[Dict]:
        with self.lock:
            return [e.to_dict() for e in list(self.events)[-limit:]]
            
    def get_current_cycle_log(self) -> List[Dict]:
        with self.lock:
            return self.pipeline_logs.get(self.current_cycle_id, [])
            
    def get_river_learning_summary(self) -> Dict:
        # Mengambil ringkasan pembelajaran River dari event terakhir
        with self.lock:
            river_events = [e for e in self.events if "River" in e.stage or "River" in e.action]
            if not river_events:
                return {"status": "No learning data yet", "confidence": 0, "recommendation": "UNKNOWN"}
            
            last_event = river_events[-1]
            return {
                "last_recommendation": last_event.details.get("recommendation", "UNKNOWN"),
                "confidence": last_event.details.get("confidence", 0),
                "reason": last_event.details.get("reason", "No specific reason"),
                "opportunity_cost_tracked": last_event.details.get("opportunity_cost", False),
                "total_learned_trades": len([e for e in river_events if e.status == "LEARNED"])
            }

    def get_darwin_status(self) -> Dict:
        with self.lock:
            darwin_events = [e for e in self.events if "Darwin" in e.action]
            if not darwin_events:
                return {"status": "Idle", "improvements": 0, "last_analysis": "Never"}
            
            last_event = darwin_events[-1]
            return {
                "status": "Active" if last_event.status == "SUCCESS" else "Analyzing",
                "improvements_made": len(darwin_events),
                "last_analysis_time": last_event.timestamp,
                "suggestion": last_event.details.get("suggestion", "None")
            }

# Singleton instance
telemetry = TelemetrySystem()
