import os
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

CONFIG_DIR = BASE_DIR / "config"
RESULTS_DIR = BASE_DIR / "results"
SCREENSHOTS_DIR = RESULTS_DIR / "screenshots"

# Ensure directories exist
CONFIG_DIR.mkdir(exist_ok=True)
RESULTS_DIR.mkdir(exist_ok=True)
SCREENSHOTS_DIR.mkdir(exist_ok=True)

class Config:
    DISPLAY_URL = os.getenv("DISPLAY_URL", "https://script.google.com/a/macros/sairamtap.edu.in/s/AKfycbyTzeQc3hyLa9lWFG6cvglRc9ch-EhSosmdXvjHy30aUA2cjqCsuRj7vQiDsz_AIiuM/exec?display=1&v=IW4111")
    HEADLESS = os.getenv("HEADLESS", "true").lower() == "true"
    PAGE_TIMEOUT = int(os.getenv("PAGE_TIMEOUT", "30000"))
    ACTION_TIMEOUT = int(os.getenv("ACTION_TIMEOUT", "10000"))
    TIMEZONE = os.getenv("TIMEZONE", "Asia/Kolkata")
    
    # Selectors for QR and Attendance (Configurable Placeholders)
    QR_SELECTOR = "iframe#sandboxFrame"   # Google apps script iframe
    QR_DESTINATION_ATTR = "src"   # Handled custom in qr_handler.py
    
    # NOTE: Since the attendance page could not be fetched due to host restrictions,
    # these are reasonable Google Forms / Apps Script defaults, but you may still need to tweak them!
    ATTENDANCE_ID_INPUT_SELECTOR = "input#studentid" # First text input is usually Student ID
    ATTENDANCE_SUBMIT_SELECTOR = "button"
    SUCCESS_MESSAGE_SELECTOR = "div#msg"  # Fallback to body text scanning
    FAILURE_MESSAGE_SELECTOR = "div#msg"
    
    # Admin Panel Protection
    ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "letmein123")
    FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "automation-secret-do-not-share")

config = Config()
