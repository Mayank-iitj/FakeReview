"""Base scraper class."""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from loguru import logger

from app.config import settings


class BaseScraper(ABC):
    """Base class for review scrapers."""
    
    def __init__(self):
        """Initialize scraper with configuration."""
        self.user_agent = UserAgent()
        self.timeout = settings.SCRAPER_TIMEOUT
        self.rate_limit = settings.SCRAPER_RATE_LIMIT
        self.max_retries = settings.SCRAPER_MAX_RETRIES
        self.driver = None
        
    def _init_driver(self) -> webdriver.Chrome:
        """
        Initialize Selenium WebDriver with anti-detection measures.
        
        Returns:
            Chrome WebDriver instance
        """
        chrome_options = Options()
        
        if settings.SCRAPER_HEADLESS:
            chrome_options.add_argument('--headless')
        
        # Anti-detection measures
        chrome_options.add_argument(f'user-agent={self.user_agent.random}')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        
        # Additional privacy settings
        chrome_options.add_argument('--disable-web-security')
        chrome_options.add_argument('--allow-running-insecure-content')
        
        driver = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()),
            options=chrome_options
        )
        
        # Execute CDP commands to hide automation
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": self.user_agent.random
        })
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver
    
    def _wait_for_element(self, by: By, value: str, timeout: Optional[int] = None) -> bool:
        """
        Wait for element to be present.
        
        Args:
            by: Selenium By locator
            value: Locator value
            timeout: Optional timeout override
            
        Returns:
            True if element found, False otherwise
        """
        try:
            WebDriverWait(self.driver, timeout or self.timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return True
        except TimeoutException:
            logger.warning(f"Element not found: {value}")
            return False
    
    def _random_delay(self, min_seconds: float = 1, max_seconds: float = 3):
        """
        Add random delay to mimic human behavior.
        
        Args:
            min_seconds: Minimum delay
            max_seconds: Maximum delay
        """
        time.sleep(random.uniform(min_seconds, max_seconds))
    
    def _scroll_page(self, scrolls: int = 3):
        """
        Scroll page to load dynamic content.
        
        Args:
            scrolls: Number of scroll actions
        """
        for _ in range(scrolls):
            self.driver.execute_script("window.scrollBy(0, 500);")
            self._random_delay(0.5, 1.5)
    
    def _retry_on_failure(self, func, *args, **kwargs):
        """
        Retry function on failure.
        
        Args:
            func: Function to retry
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result or None on failure
        """
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt < self.max_retries - 1:
                    self._random_delay(2, 5)
                else:
                    logger.error(f"All retries failed for {func.__name__}")
                    return None
    
    @abstractmethod
    def scrape_product(self, product_url: str, max_reviews: Optional[int] = None) -> List[Dict]:
        """
        Scrape reviews for a product.
        
        Args:
            product_url: Product page URL
            max_reviews: Maximum number of reviews to scrape
            
        Returns:
            List of review dictionaries
        """
        pass
    
    @abstractmethod
    def _parse_review_element(self, element) -> Dict:
        """
        Parse individual review element.
        
        Args:
            element: Review HTML element
            
        Returns:
            Review dictionary
        """
        pass
    
    def close(self):
        """Close the web driver."""
        if self.driver:
            self.driver.quit()
            logger.info("WebDriver closed")
    
    def __enter__(self):
        """Context manager entry."""
        self.driver = self._init_driver()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
