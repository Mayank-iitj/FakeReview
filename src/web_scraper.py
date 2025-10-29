"""
Web Scraper Module
Extracts product reviews from various e-commerce platforms.
"""

import re
import time
import logging
from typing import List, Dict, Optional
from urllib.parse import urlparse
import pandas as pd

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReviewScraper:
    """
    A class for scraping product reviews from various e-commerce platforms.
    """
    
    SUPPORTED_PLATFORMS = {
        'amazon': ['amazon.com', 'amazon.in', 'amazon.co.uk', 'amazon.de', 'amazon.fr'],
        'flipkart': ['flipkart.com'],
        'ebay': ['ebay.com', 'ebay.in', 'ebay.co.uk'],
    }
    
    def __init__(self, max_reviews: int = 50, delay: float = 1.0):
        """
        Initialize the ReviewScraper.
        
        Args:
            max_reviews: Maximum number of reviews to scrape
            delay: Delay between requests in seconds (to be respectful)
        """
        self.max_reviews = max_reviews
        self.delay = delay
        logger.info(f"ReviewScraper initialized (max_reviews={max_reviews}, delay={delay}s)")
    
    def identify_platform(self, url: str) -> Optional[str]:
        """
        Identify the e-commerce platform from URL.
        
        Args:
            url: Product URL
            
        Returns:
            Platform name or None if not supported
        """
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower().replace('www.', '')
            
            for platform, domains in self.SUPPORTED_PLATFORMS.items():
                if any(d in domain for d in domains):
                    return platform
            
            return None
        except Exception as e:
            logger.error(f"Error identifying platform: {str(e)}")
            return None
    
    def scrape_reviews(self, url: str) -> List[Dict[str, str]]:
        """
        Scrape reviews from the given product URL.
        
        Args:
            url: Product URL
            
        Returns:
            List of review dictionaries with 'text', 'rating', and 'date' keys
        """
        platform = self.identify_platform(url)
        
        if not platform:
            logger.warning(f"Unsupported platform for URL: {url}")
            return []
        
        logger.info(f"Detected platform: {platform}")
        
        try:
            if platform == 'amazon':
                return self._scrape_amazon(url)
            elif platform == 'flipkart':
                return self._scrape_flipkart(url)
            elif platform == 'ebay':
                return self._scrape_ebay(url)
            else:
                logger.warning(f"Platform {platform} not implemented yet")
                return []
        except Exception as e:
            logger.error(f"Error scraping reviews: {str(e)}")
            return []
    
    def _scrape_amazon(self, url: str) -> List[Dict[str, str]]:
        """
        Scrape reviews from Amazon.
        
        Note: This is a placeholder. For production use, you should:
        1. Use the Amazon Product Advertising API (requires approval)
        2. Use a dedicated scraping library like scrapy with proper headers
        3. Consider using selenium for dynamic content
        4. Respect robots.txt and rate limits
        
        Args:
            url: Amazon product URL
            
        Returns:
            List of review dictionaries
        """
        try:
            import requests
            from bs4 import BeautifulSoup
            
            # Extract ASIN from URL
            asin_match = re.search(r'/dp/([A-Z0-9]{10})', url)
            if not asin_match:
                logger.error("Could not extract ASIN from Amazon URL")
                return []
            
            asin = asin_match.group(1)
            reviews_url = f"https://www.amazon.com/product-reviews/{asin}/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept-Language': 'en-US,en;q=0.9',
            }
            
            reviews = []
            page = 1
            
            while len(reviews) < self.max_reviews and page <= 5:  # Limit to 5 pages
                try:
                    response = requests.get(reviews_url, headers=headers, timeout=10)
                    
                    if response.status_code != 200:
                        logger.warning(f"Failed to fetch page {page}: status {response.status_code}")
                        break
                    
                    soup = BeautifulSoup(response.content, 'html.parser')
                    review_divs = soup.find_all('div', {'data-hook': 'review'})
                    
                    if not review_divs:
                        logger.info("No more reviews found")
                        break
                    
                    for review_div in review_divs:
                        if len(reviews) >= self.max_reviews:
                            break
                        
                        # Extract review text
                        text_elem = review_div.find('span', {'data-hook': 'review-body'})
                        text = text_elem.get_text(strip=True) if text_elem else ""
                        
                        # Extract rating
                        rating_elem = review_div.find('i', {'data-hook': 'review-star-rating'})
                        rating = rating_elem.get_text(strip=True) if rating_elem else "N/A"
                        
                        # Extract date
                        date_elem = review_div.find('span', {'data-hook': 'review-date'})
                        date = date_elem.get_text(strip=True) if date_elem else "N/A"
                        
                        if text:
                            reviews.append({
                                'text': text,
                                'rating': rating,
                                'date': date,
                                'platform': 'Amazon'
                            })
                    
                    # Find next page
                    next_page = soup.find('li', {'class': 'a-last'})
                    if next_page and next_page.find('a'):
                        next_url = next_page.find('a')['href']
                        reviews_url = f"https://www.amazon.com{next_url}"
                        page += 1
                        time.sleep(self.delay)  # Be respectful
                    else:
                        break
                
                except Exception as e:
                    logger.error(f"Error scraping Amazon page {page}: {str(e)}")
                    break
            
            logger.info(f"Scraped {len(reviews)} reviews from Amazon")
            return reviews
        
        except ImportError:
            logger.error("Required libraries not installed. Please install: pip install requests beautifulsoup4")
            return []
        except Exception as e:
            logger.error(f"Error in Amazon scraper: {str(e)}")
            return []
    
    def _scrape_flipkart(self, url: str) -> List[Dict[str, str]]:
        """
        Scrape reviews from Flipkart.
        
        Note: Similar considerations as Amazon scraper apply.
        
        Args:
            url: Flipkart product URL
            
        Returns:
            List of review dictionaries
        """
        try:
            import requests
            from bs4 import BeautifulSoup
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code != 200:
                logger.error(f"Failed to fetch Flipkart page: status {response.status_code}")
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            reviews = []
            
            # Flipkart review selectors (may need updates as site changes)
            review_divs = soup.find_all('div', {'class': re.compile(r'.*_27M-vq.*')})
            
            for review_div in review_divs[:self.max_reviews]:
                text = review_div.get_text(strip=True)
                
                if text:
                    reviews.append({
                        'text': text,
                        'rating': 'N/A',
                        'date': 'N/A',
                        'platform': 'Flipkart'
                    })
            
            logger.info(f"Scraped {len(reviews)} reviews from Flipkart")
            return reviews
        
        except ImportError:
            logger.error("Required libraries not installed. Please install: pip install requests beautifulsoup4")
            return []
        except Exception as e:
            logger.error(f"Error in Flipkart scraper: {str(e)}")
            return []
    
    def _scrape_ebay(self, url: str) -> List[Dict[str, str]]:
        """
        Scrape reviews from eBay.
        
        Note: Similar considerations as Amazon scraper apply.
        
        Args:
            url: eBay product URL
            
        Returns:
            List of review dictionaries
        """
        logger.warning("eBay scraper not fully implemented yet")
        return []
    
    def reviews_to_dataframe(self, reviews: List[Dict[str, str]]) -> pd.DataFrame:
        """
        Convert scraped reviews to a pandas DataFrame.
        
        Args:
            reviews: List of review dictionaries
            
        Returns:
            DataFrame with review data
        """
        if not reviews:
            return pd.DataFrame(columns=['text', 'rating', 'date', 'platform'])
        
        df = pd.DataFrame(reviews)
        logger.info(f"Converted {len(df)} reviews to DataFrame")
        return df


def scrape_product_reviews(url: str, max_reviews: int = 50) -> pd.DataFrame:
    """
    Convenience function to scrape reviews and return as DataFrame.
    
    Args:
        url: Product URL
        max_reviews: Maximum number of reviews to scrape
        
    Returns:
        DataFrame with scraped reviews
    """
    scraper = ReviewScraper(max_reviews=max_reviews)
    reviews = scraper.scrape_reviews(url)
    return scraper.reviews_to_dataframe(reviews)
