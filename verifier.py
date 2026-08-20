from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError
from config import config
from logger import logger

def verify_response(page: Page) -> dict:
    """
    Verifies the response of the submission by looking at the page content.
    Returns status and message.
    """
    # Wait for either success or failure indicator to show up
    # TODO: Adapt according to the real application DOM
    try:
        import time
        start_wait = time.time()
        msg = ""
        
        while time.time() - start_wait < 15.0:
            page.wait_for_timeout(1000)
            try:
                for f in page.frames:
                    if "googleusercontent.com" in f.url:
                        # Extract the result text purely via V8 javascript bypassing UI locators
                        text = f.evaluate("document.getElementById('msg') ? document.getElementById('msg').innerText : ''")
                        if text and text.strip() != "":
                            msg = text.strip()
                            break
                if msg:
                    break
            except Exception:
                pass
                
        if not msg:
            return {"status": "ERROR", "msg": "No response message appeared in #msg div via JS evaluation"}
            
        success_keywords = ["success", "recorded", "marked", "present"]
        if any(kw in msg.lower() for kw in success_keywords):
            return {"status": "PASS", "msg": msg}
        else:
            # If there's a message but no success keywords, it's likely a failure (e.g. invalid ID)
            return {"status": "FAIL", "msg": msg}

    except PlaywrightTimeoutError:
        return {"status": "TIMEOUT", "msg": "Timeout waiting for post-submission response"}
    except Exception as e:
        return {"status": "ERROR", "msg": f"Verification error: {str(e)}"}
