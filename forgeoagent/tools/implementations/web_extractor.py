#!/usr/bin/env python3
"""
Web Extractor Tool

Simple web scraping and browser launching:
1. scrape_html(url) - Extract HTML using requests + BeautifulSoup
2. launch_browser(url) - Launch Playwright page for master worker to control
"""

import logging
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Optional Playwright import
try:
    from playwright.sync_api import sync_playwright, Page
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logger.warning("Playwright not installed.")


class WebExtractor:
    """
    Web Extractor - scrape HTML or launch browser page for master worker.
    """
    
    def __init__(self, headless: bool = False):
        """
        Initialize WebExtractor.
        
        Args:
            headless: Whether to run browser headless (False shows browser)
        """
        self.headless = headless
        self._playwright = None
        self._browser = None
    
    # =====================
    # Scraping (requests + bs4)
    # =====================
    
    def scrape_html(self, url: str, timeout: int = 30) -> Dict[str, Any]:
        """
        Scrape HTML from URL using requests + BeautifulSoup.
        
        Args:
            url: URL to scrape
            timeout: Request timeout
            
        Returns:
            Dict with: success, url, title, html, text, links, images, css, js
        """
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0'}
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.title.string if soup.title else ''
            
            # Extract CSS
            css_list = []
            for style in soup.find_all('style'):
                css_list.append({'type': 'inline', 'content': style.string or ''})
            for link in soup.find_all('link', rel='stylesheet'):
                if link.get('href'):
                    css_list.append({'type': 'external', 'url': urljoin(url, link['href'])})
            
            # Extract JS
            js_list = []
            for script in soup.find_all('script'):
                if script.get('src'):
                    js_list.append({'type': 'external', 'url': urljoin(url, script['src'])})
                elif script.string:
                    js_list.append({'type': 'inline', 'content': script.string})
            
            # Extract links
            links = [{'text': a.get_text(strip=True), 'url': urljoin(url, a['href'])} 
                     for a in soup.find_all('a', href=True)]
            
            # Extract images
            images = [{'src': urljoin(url, img['src']), 'alt': img.get('alt', '')} 
                      for img in soup.find_all('img', src=True)]
            
            return {
                'success': True,
                'url': url,
                'title': title,
                'html': response.text,
                'text': soup.get_text(separator='\n', strip=True),
                'links': links,
                'images': images,
                'css': css_list,
                'js': js_list
            }
            
        except Exception as e:
            logger.error(f"Scrape error: {e}")
            return {'success': False, 'url': url, 'error': str(e)}
    
    # =====================
    # Browser (Playwright)
    # =====================
    
    def launch_browser(self, url: str = None) -> Optional['Page']:
        """
        Launch Playwright browser and optionally navigate to URL.
        Returns the Page object for master worker to control.
        
        Args:
            url: Optional URL to navigate to
            
        Returns:
            Playwright Page object (master worker controls it)
        """
        if not PLAYWRIGHT_AVAILABLE:
            logger.error("Playwright not installed. Run: pip install playwright && playwright install")
            return None
        
        try:
            self._playwright = sync_playwright().start()
            self._browser = self._playwright.chromium.launch(headless=self.headless)
            page = self._browser.new_page()
            
            if url:
                page.goto(url, wait_until='domcontentloaded')
            
            logger.info(f"Browser launched. Page returned for master worker.")
            return page
            
        except Exception as e:
            logger.error(f"Browser launch error: {e}")
            self.close_browser()
            return None
    
    def close_browser(self):
        """Close browser and cleanup."""
        try:
            if self._browser:
                self._browser.close()
                self._browser = None
            if self._playwright:
                self._playwright.stop()
                self._playwright = None
        except Exception as e:
            logger.error(f"Close error: {e}")


if __name__ == "__main__":
    extractor = WebExtractor()
    
    # Test scraping
    print("=== Scrape Test ===")
    result = extractor.scrape_html('https://example.com')
    print(f"Title: {result.get('title')}")
    print(f"HTML length: {len(result.get('html', ''))}")
    
    # Test browser launch
    print("\n=== Browser Test ===")
    page = extractor.launch_browser('https://example.com')
    if page:
        print(f"Page title: {page.title()}")
        print(f"Page URL: {page.url}")
        # Master worker can now use page.click(), page.fill(), etc.
        import time
        # time.sleep(10)
        page.click("a")
        time.sleep(10)
        extractor.close_browser()
        print("Browser closed.")
