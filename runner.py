import datetime
import time
from config import config, SCREENSHOTS_DIR
from logger import logger, log_test_result, log_batch_summary
from models import TestResult, BatchSummary
from id_manager import get_enabled_ids
from browser import BrowserManager
from qr_handler import QRHandler
from attendance import AttendanceHandler
from scheduler import get_automation_status

def run_automation_batch(run_type: str = "MANUAL", dry_run: bool = False, specific_id: str = None):
    """
    Executes a batch automation run.
    """
    if not get_automation_status() and run_type != "DRY_RUN":
        logger.warning("Automation is disabled. Skipping run.")
        return

    logger.info(f"Starting {run_type} batch run...")
    start_time = time.time()
    
    # Get IDs
    if specific_id:
        from models import TestID
        enabled_ids = [TestID(specific_id, True)]
    else:
        enabled_ids = get_enabled_ids()
        
    if not enabled_ids:
        logger.warning("No enabled IDs found. Finishing batch.")
        return
        
    bm = BrowserManager()
    try:
        bm.start()
        
        # Open display page and get session URL
        page = bm.new_page()
        qr_handler = QRHandler(page)
        session_url = qr_handler.get_active_session_url()
        
        if not session_url:
            logger.error("Failed to obtain active session URL. Aborting batch.")
            return

        summary = BatchSummary(
            timestamp=datetime.datetime.now(),
            run_type=run_type,
            total_ids=len(enabled_ids),
            passed=0,
            failed=0,
            errors=0,
            total_duration=0.0,
            session_identifier=session_url.split('/')[-1] if '/' in session_url else session_url
        )

        attendance_handler = AttendanceHandler(page)
        
        for index, test_id in enumerate(enabled_ids, 1):
            logger.info(f"--- Processing {index}/{len(enabled_ids)}: {test_id.id} ---")
            
            result_data = attendance_handler.submit_attendance(session_url, test_id.id, dry_run=dry_run)
            status = result_data["result"]
            
            # --- Auto-Refresh Expired QR Tokens ---
            # If the Apps Script session drops mid-batch, V8 injection will TIMEOUT because the DOM form is gone.
            # OR if the server rejects it gracefully, status is FAIL but we check the message!
            is_server_expired = status == "FAIL" and "Expired" in result_data.get("message", "")
            
            if (status in ["TIMEOUT", "EXPIRED"] or is_server_expired) and not dry_run:
                logger.info(f"Timeout detected for {test_id.id}. The session URL may have expired mid-batch! Refreshing QR...")
                new_session = qr_handler.get_active_session_url()
                if new_session and new_session != session_url:
                    logger.info("Successfully fetched a new session URL. Retrying attendance...")
                    session_url = new_session
                    # Update summary tracker so we correctly log the new token
                    summary.session_identifier = session_url.split('/')[-1] if '/' in session_url else session_url
                    result_data = attendance_handler.submit_attendance(session_url, test_id.id, dry_run=dry_run)
                    status = result_data["result"]
                else:
                    logger.warning("Failed to fetch a new session URL. Falling back to screenshot generation.")
            
            screenshot_path = None
            if status in ["FAIL", "ERROR", "TIMEOUT"] and not dry_run:
                # Capture screenshot
                timestamp_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                screenshot_filename = f"{timestamp_str}_{test_id.id}_{status}.png"
                screenshot_path = str(SCREENSHOTS_DIR / screenshot_filename)
                bm.capture_screenshot(page, screenshot_path)

            test_result = TestResult(
                run_timestamp=datetime.datetime.now(),
                student_id=test_id.id,
                session_identifier=summary.session_identifier,
                result=status,
                response_message=result_data["message"],
                duration_seconds=result_data["duration"],
                screenshot_path=screenshot_path
            )
            
            log_test_result(test_result)
            
            if status == "PASS":
                summary.passed += 1
            elif status == "FAIL":
                summary.failed += 1
            else:
                summary.errors += 1
                
        summary.total_duration = time.time() - start_time
        log_batch_summary(summary)
        
    except Exception as e:
        logger.error(f"Critical error during batch run: {e}")
    finally:
        bm.close()
        logger.info("Batch run finished and browser closed.")
