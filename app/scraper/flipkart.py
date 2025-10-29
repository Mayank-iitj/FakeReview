"""Flipkart review scraper."""
from typing import List, Dict, Optional
from datetime import datetime
import re
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from loguru import logger

from app.scraper.base import BaseScraper
from app.config import settings


class FlipkartScraper(BaseScraper):
    """Scraper for Flipkart reviews."""
    
    def __init__(self):
        """Initialize Flipkart scraper."""
        super().__init__()
        self.base_url = settings.FLIPKART_BASE_URL
    
    def scrape_product(self, product_url: str, max_reviews: Optional[int] = None) -> List[Dict]:
        """
        Scrape reviews for a Flipkart product.
        
        Args:
            product_url: Flipkart product page URL
            max_reviews: Maximum number of reviews to scrape
            
        Returns:
            List of review dictionaries
        """
        logger.info(f"Starting Flipkart scrape: {product_url}")
        
        reviews = []
        
        try:
            # Navigate to product page
            self.driver.get(product_url)
            self._random_delay(2, 4)
            
            # Close login popup if it appears
            self._close_login_popup()
            
            # Extract product info
            product_info = self._extract_product_info()
            
            # Scroll to load reviews
            self._scroll_page(5)
            
            # Parse reviews
            page_reviews = self._parse_reviews_page(product_info)
            reviews.extend(page_reviews)
            
            logger.info(f"Scraped {len(page_reviews)} reviews")
            
            # Try to load more reviews
            while max_reviews is None or len(reviews) < max_reviews:
                if not self._load_more_reviews():
                    break
                
                self._random_delay(self.rate_limit, self.rate_limit + 2)
                page_reviews = self._parse_reviews_page(product_info)
                new_reviews = [r for r in page_reviews if r not in reviews]
                
                if not new_reviews:
                    break
                
                reviews.extend(new_reviews)
                logger.info(f"Total reviews scraped: {len(reviews)}")
        
        except Exception as e:
            logger.error(f"Error scraping Flipkart reviews: {e}", exc_info=True)
        
        logger.info(f"Total reviews scraped: {len(reviews)}")
        return reviews[:max_reviews] if max_reviews else reviews
    
    def _close_login_popup(self):
        """Close login popup if present."""
        try:
            close_button = self.driver.find_element(
                By.CSS_SELECTOR,
                'button._2KpZ6l._2doB4z'
            )
            close_button.click()
            self._random_delay(1, 2)
        except Exception:
            pass  # No popup present
    
    def _extract_product_info(self) -> Dict:
        """
        Extract product information from product page.
        
        Returns:
            Dictionary with product info
        """
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        
        product_info = {
            'platform': 'flipkart',
            'product_url': self.driver.current_url,
            'product_id': self._extract_product_id(self.driver.current_url),
            'product_name': '',
        }
        
        # Extract product name
        title_elem = soup.select_one('.B_NuCI')
        if title_elem:
            product_info['product_name'] = title_elem.get_text(strip=True)
        
        return product_info
    
    def _extract_product_id(self, url: str) -> str:
        """
        Extract product ID from Flipkart URL.
        
        Args:
            url: Flipkart product URL
            
        Returns:
            Product ID
        """
        match = re.search(r'pid=([A-Z0-9]+)', url)
        return match.group(1) if match else ''
    
    def _parse_reviews_page(self, product_info: Dict) -> List[Dict]:
        """
        Parse all reviews on current page.
        
        Args:
            product_info: Product information dictionary
            
        Returns:
            List of review dictionaries
        """
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        review_elements = soup.select('div._1PBCrt')
        
        reviews = []
        for element in review_elements:
            try:
                review = self._parse_review_element(element)
                review.update(product_info)
                reviews.append(review)
            except Exception as e:
                logger.warning(f"Error parsing review: {e}")
                continue
        
        return reviews
    
    def _parse_review_element(self, element) -> Dict:
        """
        Parse individual Flipkart review element.
        
        Args:
            element: BeautifulSoup review element
            
        Returns:
            Review dictionary
        """
        review = {}
        
        # Review ID (generate from reviewer name + date)
        reviewer_elem = element.select_one('._2sOITG')
        date_elem = element.select_one('._3pgR56')
        if reviewer_elem and date_elem:
            review['review_id'] = f"flipkart_{hash(reviewer_elem.get_text() + date_elem.get_text())}"
        else:
            review['review_id'] = f"flipkart_{hash(str(element))}"
        
        # Rating
        rating_elem = element.select_one('._3LWZlK')
        if rating_elem:
            rating_text = rating_elem.get_text(strip=True)
            match = re.search(r'(\d+)', rating_text)
            review['rating'] = float(match.group(1)) if match else 0.0
        else:
            review['rating'] = 0.0
        
        # Title
        title_elem = element.select_one('._2xg6Ul')
        review['review_title'] = title_elem.get_text(strip=True) if title_elem else ''
        
        # Text
        text_elem = element.select_one('.t-ZTKy')
        if not text_elem:
            text_elem = element.select_one('._11pzQk')
        review['review_text'] = text_elem.get_text(strip=True) if text_elem else ''
        
        # Reviewer name
        review['reviewer_name'] = reviewer_elem.get_text(strip=True) if reviewer_elem else ''
        review['reviewer_id'] = review['reviewer_name'].replace(' ', '_').lower()
        
        # Reviewer profile URL (Flipkart doesn't provide direct links)
        review['reviewer_profile_url'] = ''
        
        # Review date
        if date_elem:
            date_text = date_elem.get_text(strip=True)
            review['review_date'] = self._parse_date(date_text)
        else:
            review['review_date'] = None
        
        # Verified purchase (Flipkart shows "Certified Buyer")
        certified_elem = element.select_one('._3LYOAd')
        review['verified_purchase'] = certified_elem is not None
        
        # Helpful count
        helpful_elem = element.select_one('._1_BQL8')
        if helpful_elem:
            helpful_text = helpful_elem.get_text(strip=True)
            match = re.search(r'(\d+)', helpful_text)
            review['helpful_count'] = int(match.group(1)) if match else 0
        else:
            review['helpful_count'] = 0
        
        return review
    
    def _parse_date(self, date_text: str) -> Optional[datetime]:
        """
        Parse Flipkart date string.
        
        Args:
            date_text: Date string from Flipkart
            
        Returns:
            datetime object or None
        """
        try:
            # Flipkart format: "21 Jan, 2024" or "21 Jan"
            date_text = date_text.strip()
            
            # Add current year if not present
            if ',' not in date_text:
                date_text = f"{date_text}, {datetime.now().year}"
            
            return datetime.strptime(date_text, '%d %b, %Y')
        except Exception as e:
            logger.warning(f"Could not parse date '{date_text}': {e}")
        
        return None
    
    def _load_more_reviews(self) -> bool:
        """
        Click "View More" to load more reviews.
        
        Returns:
            True if successful, False if no button found
        """
        try:
            load_more_button = self.driver.find_element(
                By.CSS_SELECTOR,
                '._1i2dFb'
            )
            load_more_button.click()
            self._random_delay(2, 4)
            return True
        except Exception:
            return False
