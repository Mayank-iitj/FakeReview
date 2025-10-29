"""Amazon review scraper."""
from typing import List, Dict, Optional
from datetime import datetime
import re
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from loguru import logger

from app.scraper.base import BaseScraper
from app.config import settings


class AmazonScraper(BaseScraper):
    """Scraper for Amazon reviews."""
    
    def __init__(self):
        """Initialize Amazon scraper."""
        super().__init__()
        self.base_url = settings.AMAZON_BASE_URL
    
    def scrape_product(self, product_url: str, max_reviews: Optional[int] = None) -> List[Dict]:
        """
        Scrape reviews for an Amazon product.
        
        Args:
            product_url: Amazon product page URL
            max_reviews: Maximum number of reviews to scrape
            
        Returns:
            List of review dictionaries
        """
        logger.info(f"Starting Amazon scrape: {product_url}")
        
        reviews = []
        
        try:
            # Navigate to product page
            self.driver.get(product_url)
            self._random_delay(2, 4)
            
            # Extract product info
            product_info = self._extract_product_info()
            
            # Click "See all reviews" button
            if not self._navigate_to_reviews():
                logger.warning("Could not navigate to reviews page")
                return reviews
            
            # Scrape reviews from multiple pages
            page = 1
            while True:
                logger.info(f"Scraping page {page}")
                
                # Wait for reviews to load
                if not self._wait_for_element(By.CSS_SELECTOR, '[data-hook="review"]', timeout=10):
                    logger.warning("No reviews found on page")
                    break
                
                # Parse reviews on current page
                page_reviews = self._parse_reviews_page(product_info)
                reviews.extend(page_reviews)
                
                logger.info(f"Scraped {len(page_reviews)} reviews from page {page}")
                
                # Check if we've reached the limit
                if max_reviews and len(reviews) >= max_reviews:
                    reviews = reviews[:max_reviews]
                    break
                
                # Navigate to next page
                if not self._go_to_next_page():
                    logger.info("No more pages available")
                    break
                
                page += 1
                self._random_delay(self.rate_limit, self.rate_limit + 2)
        
        except Exception as e:
            logger.error(f"Error scraping Amazon reviews: {e}", exc_info=True)
        
        logger.info(f"Total reviews scraped: {len(reviews)}")
        return reviews
    
    def _extract_product_info(self) -> Dict:
        """
        Extract product information from product page.
        
        Returns:
            Dictionary with product info
        """
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        
        product_info = {
            'platform': 'amazon',
            'product_url': self.driver.current_url,
            'product_id': self._extract_product_id(self.driver.current_url),
            'product_name': '',
        }
        
        # Extract product name
        title_elem = soup.select_one('#productTitle')
        if title_elem:
            product_info['product_name'] = title_elem.get_text(strip=True)
        
        return product_info
    
    def _extract_product_id(self, url: str) -> str:
        """
        Extract ASIN from Amazon URL.
        
        Args:
            url: Amazon product URL
            
        Returns:
            Product ID (ASIN)
        """
        match = re.search(r'/dp/([A-Z0-9]{10})', url)
        return match.group(1) if match else ''
    
    def _navigate_to_reviews(self) -> bool:
        """
        Navigate to all reviews page.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Look for "See all reviews" link
            see_all_link = self.driver.find_element(
                By.CSS_SELECTOR, 
                '[data-hook="see-all-reviews-link-foot"]'
            )
            see_all_link.click()
            self._random_delay(2, 4)
            return True
        except Exception as e:
            logger.warning(f"Could not find 'See all reviews' link: {e}")
            return False
    
    def _parse_reviews_page(self, product_info: Dict) -> List[Dict]:
        """
        Parse all reviews on current page.
        
        Args:
            product_info: Product information dictionary
            
        Returns:
            List of review dictionaries
        """
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        review_elements = soup.select('[data-hook="review"]')
        
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
        Parse individual Amazon review element.
        
        Args:
            element: BeautifulSoup review element
            
        Returns:
            Review dictionary
        """
        review = {}
        
        # Review ID
        review_id_elem = element.get('id')
        review['review_id'] = review_id_elem if review_id_elem else ''
        
        # Rating
        rating_elem = element.select_one('[data-hook="review-star-rating"]')
        if rating_elem:
            rating_text = rating_elem.get_text(strip=True)
            match = re.search(r'(\d+\.?\d*)', rating_text)
            review['rating'] = float(match.group(1)) if match else 0.0
        else:
            review['rating'] = 0.0
        
        # Title
        title_elem = element.select_one('[data-hook="review-title"]')
        review['review_title'] = title_elem.get_text(strip=True) if title_elem else ''
        
        # Text
        text_elem = element.select_one('[data-hook="review-body"]')
        review['review_text'] = text_elem.get_text(strip=True) if text_elem else ''
        
        # Reviewer name
        author_elem = element.select_one('.a-profile-name')
        review['reviewer_name'] = author_elem.get_text(strip=True) if author_elem else ''
        
        # Reviewer profile URL
        profile_elem = element.select_one('.a-profile')
        if profile_elem and profile_elem.get('href'):
            review['reviewer_profile_url'] = self.base_url + profile_elem.get('href')
            # Extract reviewer ID from URL
            match = re.search(r'/profile/([^/]+)', profile_elem.get('href'))
            review['reviewer_id'] = match.group(1) if match else ''
        else:
            review['reviewer_profile_url'] = ''
            review['reviewer_id'] = ''
        
        # Review date
        date_elem = element.select_one('[data-hook="review-date"]')
        if date_elem:
            date_text = date_elem.get_text(strip=True)
            review['review_date'] = self._parse_date(date_text)
        else:
            review['review_date'] = None
        
        # Verified purchase
        verified_elem = element.select_one('[data-hook="avp-badge"]')
        review['verified_purchase'] = verified_elem is not None
        
        # Helpful count
        helpful_elem = element.select_one('[data-hook="helpful-vote-statement"]')
        if helpful_elem:
            helpful_text = helpful_elem.get_text(strip=True)
            match = re.search(r'(\d+)', helpful_text)
            review['helpful_count'] = int(match.group(1)) if match else 0
        else:
            review['helpful_count'] = 0
        
        return review
    
    def _parse_date(self, date_text: str) -> Optional[datetime]:
        """
        Parse Amazon date string.
        
        Args:
            date_text: Date string from Amazon
            
        Returns:
            datetime object or None
        """
        try:
            # Amazon format: "Reviewed in the United States on January 1, 2024"
            match = re.search(r'on\s+(.+)$', date_text)
            if match:
                date_str = match.group(1)
                return datetime.strptime(date_str, '%B %d, %Y')
        except Exception as e:
            logger.warning(f"Could not parse date '{date_text}': {e}")
        
        return None
    
    def _go_to_next_page(self) -> bool:
        """
        Navigate to next reviews page.
        
        Returns:
            True if successful, False if no next page
        """
        try:
            next_button = self.driver.find_element(
                By.CSS_SELECTOR,
                '.a-pagination .a-last:not(.a-disabled) a'
            )
            next_button.click()
            self._random_delay(2, 4)
            return True
        except Exception:
            return False
