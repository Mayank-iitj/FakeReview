"""Scraper API endpoints."""
from fastapi import APIRouter, HTTPException
from typing import Optional, List
import asyncio
from loguru import logger

from app.scraper import AmazonScraper, FlipkartScraper

router = APIRouter()


@router.post("/scrape/amazon")
async def scrape_amazon(
    product_url: str,
    max_reviews: Optional[int] = None
):
    """
    Scrape reviews from Amazon product.
    
    Args:
        product_url: Amazon product URL
        max_reviews: Maximum reviews to scrape
        
    Returns:
        Scraped reviews list
    """
    logger.info(f"Starting Amazon scrape: {product_url}")
    
    try:
        scraper = AmazonScraper()
        reviews = scraper.scrape_product(product_url, max_reviews)
        scraper.close()
        
        return {
            'platform': 'amazon',
            'product_url': product_url,
            'total_reviews': len(reviews),
            'reviews': reviews[:min(10, len(reviews))]  # Return first 10 as sample
        }
    
    except Exception as e:
        logger.error(f"Error scraping Amazon: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/scrape/flipkart")
async def scrape_flipkart(
    product_url: str,
    max_reviews: Optional[int] = None
):
    """
    Scrape reviews from Flipkart product.
    
    Args:
        product_url: Flipkart product URL
        max_reviews: Maximum reviews to scrape
        
    Returns:
        Scraped reviews list
    """
    logger.info(f"Starting Flipkart scrape: {product_url}")
    
    try:
        scraper = FlipkartScraper()
        reviews = scraper.scrape_product(product_url, max_reviews)
        scraper.close()
        
        return {
            'platform': 'flipkart',
            'product_url': product_url,
            'total_reviews': len(reviews),
            'reviews': reviews[:min(10, len(reviews))]  # Return first 10 as sample
        }
    
    except Exception as e:
        logger.error(f"Error scraping Flipkart: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
