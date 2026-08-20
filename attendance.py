from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError
from config import config
from logger import logger
from verifier import verify_response
import time

class AttendanceHandler:
    def __init__(self, page: Page):
        self.page = page

    def submit_attendance(self, session_url: str, student_id: str, dry_run: bool = False) -> dict:
        """
        Navigates to the session URL, enters ID, and submits the form.
        """
        start_time = time.time()
        result = {
            "result": "ERROR",
            "message": "Unknown error",
            "duration": 0.0
        }
        
        try:
            logger.info(f"Navigating to session URL for {student_id}...")
            try:
                self.page.goto(session_url, wait_until="commit", timeout=config.PAGE_TIMEOUT)
            except Exception as nav_e:
                logger.warning(f"Navigation timed out, but proceeding to form anyway: {nav_e}")
            
            logger.info("Waiting for Google Apps Script iframe to load...")
            
            # Poll executing javascript directly in the sandbox frame
            start_wait = time.time()
            success = False
            
            while time.time() - start_wait < 15.0:
                self.page.wait_for_timeout(1000)
                try:
                    for f in self.page.frames:
                        if "googleusercontent.com" in f.url:
                            # Try to execute JS directly in the frame execution context
                            # This bypasses all strict cross-origin UI visibility checks!
                            is_expired = f.evaluate("document.body.innerText.includes('QR Code Expired')")
                            if is_expired:
                                logger.warning(f"Detected EXPIRED QR code text for {student_id} directly on screen.")
                                result["result"] = "EXPIRED"
                                result["message"] = "QR Code Expired. Please scan latest QR."
                                result["duration"] = time.time() - start_time
                                return result
                            
                            is_ready = f.evaluate("document.getElementById('studentid') !== null")
                            if is_ready:
                                logger.info(f"Injecting Javascript to submit attendance for {student_id}")
                                f.evaluate(f"document.getElementById('studentid').value = '{student_id}';")
                                
                                if dry_run:
                                    logger.info(f"[DRY RUN] Skipping JS submitAttendance() for {student_id}")
                                else:
                                    f.evaluate("if(typeof submitAttendance === 'function') submitAttendance();")
                                    
                                success = True
                                break
                    if success:
                        break
                except Exception:
                    # Ignore javascript exception and retry (e.g. frame disconnected during load)
                    pass
            
            if not success:
                raise PlaywrightTimeoutError("Could not render the iframe content via JS evaluation")
                
            if dry_run:
                result["result"] = "PASS"
                result["message"] = "Dry run successful"
                result["duration"] = time.time() - start_time
                return result
            
            # Wait for verification (handled by verifier)
            verification = verify_response(self.page)
            result["result"] = verification["status"]
            result["message"] = verification["msg"]
            
        except PlaywrightTimeoutError:
            logger.error(f"Timeout submitting attendance for {student_id}")
            result["result"] = "TIMEOUT"
            result["message"] = "Page load or element wait timeout"
            
            # Dump the current HTML and a screenshot for deep debugging!
            try:
                self.page.screenshot(path=f"results/screenshots/{student_id}_timeout_debug.png")
                logger.error(f"Saved timeout screenshot to {student_id}_timeout_debug.png")
                with open(f"results/{student_id}_timeout_debug.html", "w", encoding="utf-8") as f:
                    f.write(self.page.content())
                logger.error(f"Saved raw HTML to results/{student_id}_timeout_debug.html")
            except Exception as dump_e:
                 logger.error(f"Could not dump debug files: {dump_e}")
                 
        except Exception as e:
            logger.error(f"Error submitting attendance for {student_id}: {e}")
            result["result"] = "ERROR"
            result["message"] = str(e)
            
        result["duration"] = time.time() - start_time
        return result
