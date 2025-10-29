"""
URL Reviews Scraper
Lightweight, Streamlit-friendly scraper for product reviews from common e-commerce sites.
No system dependencies; uses requests + BeautifulSoup(html.parser).
"""
from __future__ import annotations

import logging
import re
import time
from dataclasses import dataclass
from typing import List, Dict, Optional
from urllib.parse import urlparse, urlunparse, urlencode, parse_qsl

import requests
import pandas as pd
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


@dataclass
class ScrapeOptions:
    max_reviews: int = 50
    delay_seconds: float = 1.0
    timeout: int = 15


class ReviewScraper:
    SUPPORTED_PLATFORMS = {
        "amazon": ["amazon.com", "amazon.in", "amazon.co.uk", "amazon.de", "amazon.fr"],
        "flipkart": ["flipkart.com"],
        "ebay": ["ebay.com", "ebay.in", "ebay.co.uk"],
    }

    def __init__(self, options: Optional[ScrapeOptions] = None):
        self.options = options or ScrapeOptions()
        logger.info(
            "ReviewScraper initialized (max_reviews=%s, delay=%.1fs)",
            self.options.max_reviews,
            self.options.delay_seconds,
        )

    def identify_platform(self, url: str) -> Optional[str]:
        try:
            domain = urlparse(url).netloc.lower().replace("www.", "")
            for platform, domains in self.SUPPORTED_PLATFORMS.items():
                if any(domain.endswith(d) for d in domains):
                    return platform
        except Exception as e:
            logger.error("identify_platform error: %s", e)
        return None

    def _get(self, url: str) -> Optional[BeautifulSoup]:
        try:
            resp = requests.get(url, headers=DEFAULT_HEADERS, timeout=self.options.timeout)
            if resp.status_code != 200:
                logger.warning("GET %s -> %s", url, resp.status_code)
                return None
            return BeautifulSoup(resp.text, "html.parser")
        except Exception as e:
            logger.error("HTTP error for %s: %s", url, e)
            return None

    def scrape_reviews(self, url: str) -> List[Dict[str, str]]:
        platform = self.identify_platform(url)
        if not platform:
            logger.warning("Unsupported platform for URL: %s", url)
            return []
        if platform == "amazon":
            return self._scrape_amazon(url)
        if platform == "flipkart":
            return self._scrape_flipkart(url)
        if platform == "ebay":
            return self._scrape_ebay(url)
        return []

    # -------------------- Amazon --------------------
    def _asin_from_url(self, url: str) -> Optional[str]:
        # Try common patterns: /dp/ASIN, /gp/product/ASIN
        for pat in [r"/dp/([A-Z0-9]{10})", r"/gp/product/([A-Z0-9]{10})", r"/product-reviews/([A-Z0-9]{10})"]:
            m = re.search(pat, url)
            if m:
                return m.group(1)
        return None

    def _domain(self, url: str) -> str:
        parsed = urlparse(url)
        return parsed.netloc.lower().replace("www.", "")

    def _amazon_reviews_url(self, url: str, asin: str, page: int = 1) -> str:
        domain = self._domain(url)
        base = f"https://{domain}/product-reviews/{asin}"
        params = {
            "ie": "UTF8",
            "reviewerType": "all_reviews",
            "pageNumber": str(page),
        }
        return f"{base}/?{urlencode(params)}"

    def _scrape_amazon(self, url: str) -> List[Dict[str, str]]:
        asin = self._asin_from_url(url)
        if not asin:
            logger.error("Could not extract ASIN from Amazon URL")
            return []

        reviews: List[Dict[str, str]] = []
        page = 1
        max_pages = 5
        while len(reviews) < self.options.max_reviews and page <= max_pages:
            page_url = self._amazon_reviews_url(url, asin, page)
            soup = self._get(page_url)
            if not soup:
                break

            blocks = soup.find_all("div", {"data-hook": "review"})
            if not blocks:
                logger.info("Amazon: no review blocks on page %s", page)
                break

            for div in blocks:
                if len(reviews) >= self.options.max_reviews:
                    break
                # Text
                text_node = div.find("span", {"data-hook": "review-body"})
                text = (text_node.get_text(strip=True) if text_node else "")
                # Rating (e.g., '5.0 out of 5 stars')
                rating_node = div.find("i", {"data-hook": "review-star-rating"}) or div.find(
                    "i", {"data-hook": "cmps-review-star-rating"}
                )
                rating = rating_node.get_text(strip=True) if rating_node else "N/A"
                # Date
                date_node = div.find("span", {"data-hook": "review-date"})
                date = date_node.get_text(strip=True) if date_node else "N/A"

                if text:
                    reviews.append({
                        "text": text,
                        "rating": rating,
                        "date": date,
                        "platform": "Amazon",
                    })

            page += 1
            time.sleep(self.options.delay_seconds)

        logger.info("Amazon: scraped %s reviews", len(reviews))
        return reviews

    # -------------------- Flipkart --------------------
    def _flipkart_reviews_url(self, url: str) -> str:
        # Flipkart often includes review tabs on the same page; use the given URL
        return url

    def _scrape_flipkart(self, url: str) -> List[Dict[str, str]]:
        soup = self._get(self._flipkart_reviews_url(url))
        if not soup:
            return []

        reviews: List[Dict[str, str]] = []
        # Common review container heuristics (Flipkart classes change frequently)
        # Try multiple selectors and collect text
        selectors = [
            ("div", {"class": re.compile(r"(?i)ZmyHeo|_27M-vq|review|t-ZTKy")}),
            ("div", {"data-hook": "review"}),
            ("p", {"class": re.compile(r"(?i)\breview\b")}),
        ]
        for name, attrs in selectors:
            for node in soup.find_all(name, attrs):
                text = node.get_text(" ", strip=True)
                if text and len(text.split()) > 3:
                    reviews.append({
                        "text": text,
                        "rating": "N/A",
                        "date": "N/A",
                        "platform": "Flipkart",
                    })
                if len(reviews) >= self.options.max_reviews:
                    break
            if len(reviews) >= self.options.max_reviews:
                break

        logger.info("Flipkart: scraped %s reviews", len(reviews))
        return reviews

    # -------------------- eBay --------------------
    def _scrape_ebay(self, url: str) -> List[Dict[str, str]]:
        soup = self._get(url)
        if not soup:
            return []
        reviews: List[Dict[str, str]] = []
        # Try common selectors
        blocks = soup.select(".ebay-review-section, .rvw, [itemprop='review']")
        for b in blocks:
            text = b.get_text(" ", strip=True)
            if text and len(text.split()) > 3:
                reviews.append({
                    "text": text,
                    "rating": "N/A",
                    "date": "N/A",
                    "platform": "eBay",
                })
            if len(reviews) >= self.options.max_reviews:
                break
        logger.info("eBay: scraped %s reviews", len(reviews))
        return reviews

    # -------------------- Utility --------------------
    def reviews_to_dataframe(self, reviews: List[Dict[str, str]]) -> pd.DataFrame:
        if not reviews:
            return pd.DataFrame(columns=["text", "rating", "date", "platform"])
        return pd.DataFrame(reviews)


def scrape_product_reviews(url: str, max_reviews: int = 50, delay_seconds: float = 1.0) -> pd.DataFrame:
    scraper = ReviewScraper(ScrapeOptions(max_reviews=max_reviews, delay_seconds=delay_seconds))
    data = scraper.scrape_reviews(url)
    return scraper.reviews_to_dataframe(data)
