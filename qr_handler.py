from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError
from config import config
from logger import logger

class QRHandler:
    def __init__(self, page: Page):
        self.page = page

    def get_active_session_url(self) -> str:
        """
        Navigates to the DISPLAY_URL and extracts the current active session/destination URL.
        """
        logger.info(f"Navigating to QR display URL: {config.DISPLAY_URL}")
        try:
            logger.info("Sniffing network traffic for the QR image request...")
            import re
            import urllib.parse
            
            # The most robust way to bypass cross-origin iframes and obfuscation is 
            # simply to watch the browser's raw network requests for the image!
            try:
                with self.page.expect_request(re.compile(r"quickchart\.io"), timeout=30000) as request_info:
                    try:
                        self.page.goto(config.DISPLAY_URL, wait_until="commit", timeout=config.PAGE_TIMEOUT)
                    except Exception as nav_e:
                        logger.warning(f"Navigation timed out, but proceeding to wait for network request: {nav_e}")
                
                qr_url = request_info.value.url
                logger.info("Network request to quickchart caught successfully!")
            except Exception as e:
                self.page.screenshot(path="results/qr_debug.png")
                logger.error("Could not capture the network request to QuickChart!")
                raise ValueError("Timeout waiting for QR image network request") from e
                
            parsed = urllib.parse.urlparse(qr_url)
            qs = urllib.parse.parse_qs(parsed.query)
            session_url = qs.get("text", [None])[0]
            
            if not session_url:
                raise ValueError("Could not parse 'text' parameter from quickchart URL.")
                
            logger.info(f"Extracted session URL: {session_url}")
            return session_url
            
        except PlaywrightTimeoutError:
            logger.error(f"Timeout waiting for QR display load at {config.DISPLAY_URL}")
            return None
        except Exception as e:
            logger.error(f"Error extracting active session URL: {e}")
            return None
