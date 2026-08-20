import logging
import csv
import json
import os
from pathlib import Path
from datetime import datetime
from config import RESULTS_DIR
from models import TestResult, BatchSummary

# Console and File Logger setup
logger = logging.getLogger("attendance_tester")
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)

fh = logging.FileHandler(RESULTS_DIR / "app.log")
fh.setFormatter(formatter)
logger.addHandler(fh)

def safe_write_csv(row: list, filepath: Path):
    """Safely append a row to a CSV file."""
    mode = 'a' if filepath.exists() else 'w'
    with open(filepath, mode, newline='', encoding='utf-8') as f:
        # Cross-platform file locking approximation for simple concurrency
        # In Python stdlib, fcntl is Unix only, so we'll just write normally 
        # since this is a local app (or use a package like filelock if strictly needed).
        # We will use simple appending for now.
        writer = csv.writer(f)
        if mode == 'w':
            writer.writerow(["run_timestamp", "student_id", "session_identifier", "result", "response_message", "duration_seconds", "screenshot_path", "error"])
        writer.writerow(row)

def safe_read_json(filepath: Path, default=None):
    if not filepath.exists():
        return default if default is not None else {}
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return default if default is not None else {}

def safe_write_json(data: dict, filepath: Path):
    tmp_path = filepath.with_suffix('.tmp')
    with open(tmp_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
    tmp_path.replace(filepath)

def log_test_result(result: TestResult):
    csv_path = RESULTS_DIR / "test_results.csv"
    row = [
        result.run_timestamp.isoformat(),
        result.student_id,
        result.session_identifier,
        result.result,
        result.response_message,
        round(result.duration_seconds, 2),
        result.screenshot_path or "",
        result.error or ""
    ]
    safe_write_csv(row, csv_path)
    logger.info(f"Result for {result.student_id}: {result.result} - {result.response_message}")

def log_batch_summary(summary: BatchSummary):
    logger.info("=" * 40)
    logger.info("BATCH COMPLETE")
    logger.info("=" * 40)
    logger.info(f"Run Type: {summary.run_type}")
    logger.info(f"Session: {summary.session_identifier}")
    logger.info(f"Total Enabled IDs: {summary.total_ids}")
    logger.info(f"Passed: {summary.passed}")
    logger.info(f"Failed: {summary.failed}")
    logger.info(f"Errors: {summary.errors}")
    logger.info(f"Total Duration: {summary.total_duration:.2f} seconds")
    if summary.total_ids > 0:
        logger.info(f"Average Duration: {summary.total_duration / summary.total_ids:.2f} seconds")
    logger.info("=" * 40)
    
    # Update daily summary
    daily_path = RESULTS_DIR / "daily_summary.json"
    daily = safe_read_json(daily_path, default={
        "total_runs": 0,
        "completed_runs": 0,
        "skipped_runs": 0,
        "total_id_tests": 0,
        "passed": 0,
        "failed": 0,
        "errors": 0,
        "total_duration": 0.0,
        "sessions_used": []
    })
    
    daily["total_runs"] += 1
    if summary.total_ids > 0:
        daily["completed_runs"] += 1
        daily["total_id_tests"] += summary.total_ids
        daily["passed"] += summary.passed
        daily["failed"] += summary.failed
        daily["errors"] += summary.errors
        daily["total_duration"] += summary.total_duration
        if summary.session_identifier not in daily["sessions_used"]:
            daily["sessions_used"].append(summary.session_identifier)
            
    safe_write_json(daily, daily_path)
