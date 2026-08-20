from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page
from config import config
from logger import logger

class BrowserManager:
    def __init__(self):
        self.playwright = None
        self.browser: Browser = None
        self.context: BrowserContext = None
        
    def start(self):
        """Initialize playwright and browser context."""
        logger.info("Starting browser...")
        self.playwright = sync_playwright().start()
        
        self.browser = self.playwright.chromium.launch(
            channel="chrome",
            headless=config.HEADLESS
        )
        self.context = self.browser.new_context(
            timezone_id=config.TIMEZONE,
            viewport={'width': 1280, 'height': 720}
        )
        logger.info("Browser started successfully.")
        
    def new_page(self) -> Page:
        """Create a new page."""
        if not self.context:
            raise Exception("Browser context not initialized. Call start() first.")
        page = self.context.new_page()
        page.set_default_timeout(config.PAGE_TIMEOUT)
        return page

    def capture_screenshot(self, page: Page, filepath: str):
        """Capture screenshot on failure."""
        try:
            page.screenshot(path=filepath, full_page=True)
            logger.info(f"Screenshot saved to {filepath}")
        except Exception as e:
            logger.error(f"Failed to capture screenshot: {e}")

    def close(self):
        """Close browser and context."""
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        logger.info("Browser closed.")
