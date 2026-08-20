from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class TestID:
    id: str
    enabled: bool

@dataclass
class TestResult:
    run_timestamp: datetime
    student_id: str
    session_identifier: str
    result: str  # PASS, FAIL, ERROR, TIMEOUT
    response_message: str
    duration_seconds: float
    screenshot_path: Optional[str] = None
    error: Optional[str] = None

@dataclass
class BatchSummary:
    timestamp: datetime
    run_type: str  # MANUAL, SCHEDULED
    total_ids: int
    passed: int
    failed: int
    errors: int
    total_duration: float
    session_identifier: str
