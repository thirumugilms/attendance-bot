import time
import datetime
import pytz
from typing import List, Set
from pathlib import Path
from config import CONFIG_DIR
from logger import logger, safe_read_json, safe_write_json

SCHEDULE_PATH = CONFIG_DIR / "schedule.json"
SETTINGS_PATH = CONFIG_DIR / "settings.json"

def get_automation_status() -> bool:
    data = safe_read_json(SETTINGS_PATH, default={"automation_enabled": True})
    return data.get("automation_enabled", True)

def set_automation_status(enabled: bool):
    data = safe_read_json(SETTINGS_PATH, default={})
    data["automation_enabled"] = enabled
    safe_write_json(data, SETTINGS_PATH)

def get_schedule() -> dict:
    return safe_read_json(SCHEDULE_PATH, default={
        "enabled": True,
        "times": ["09:00", "10:00", "11:00", "12:00"],
        "timezone": "Asia/Kolkata"
    })

def set_schedule(times: List[str], enabled: bool, timezone: str = "Asia/Kolkata"):
    data = {
        "enabled": enabled,
        "times": times,
        "timezone": timezone
    }
    safe_write_json(data, SCHEDULE_PATH)

class Scheduler:
    def __init__(self, run_callback):
        self.run_callback = run_callback
        self.executed_today: Set[str] = set()
        self.current_date = None
        self.is_running = False

    def start(self):
        self.is_running = True
        logger.info("Scheduler started.")
        try:
            while self.is_running:
                self.check_schedule()
                time.sleep(30)  # Check every 30 seconds to avoid busy waiting
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user.")
        finally:
            self.stop()
            
    def stop(self):
        self.is_running = False
        logger.info("Scheduler stopped.")

    def check_schedule(self):
        if not get_automation_status():
            return
            
        schedule = get_schedule()
        if not schedule.get("enabled", True):
            return
            
        tz_name = schedule.get("timezone", "Asia/Kolkata")
        tz = pytz.timezone(tz_name)
        now = datetime.datetime.now(tz)
        today_date = now.date()
        
        # Reset executions on a new day
        if self.current_date != today_date:
            self.current_date = today_date
            self.executed_today.clear()
            
        current_time_str = now.strftime("%H:%M")
        
        times = schedule.get("times", [])
        
        if current_time_str in times and current_time_str not in self.executed_today:
            logger.info(f"Scheduled time reached: {current_time_str}")
            self.executed_today.add(current_time_str)
            
            try:
                self.run_callback(run_type="SCHEDULED")
            except Exception as e:
                logger.error(f"Error executing scheduled run: {e}")
