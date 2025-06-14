"""
Web Scraper Module

A comprehensive web scraping solution following best practices and scientific methods.
This module provides robust functionality for extracting data from websites while
respecting rate limits and implementing proper error handling.

Author: Web Scraper Project
Date: 2024
"""

import requests
import time
import random
import logging
from typing import Dict, List, Optional, Union, Any
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser
import json
import csv
import os
from datetime import datetime

# Import configuration
from config import config

# BeautifulSoup for HTML parsing
from bs4 import BeautifulSoup

# Selenium for dynamic content (optional)
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("Selenium not available. Dynamic content scraping will be disabled.")

# User agent rotation
try:
    from fake_useragent import UserAgent
    USER_AGENT_AVAILABLE = True
except ImportError:
    USER_AGENT_AVAILABLE = False
    print("fake-useragent not available. Using default user agent.")

# Environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
    ENV_AVAILABLE = True
except ImportError:
    ENV_AVAILABLE = False
    print("python-dotenv not available. Environment variables not loaded.")

# Data manipulation
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    print("pandas not available. CSV export will use basic functionality.")

# Configure logging based on config
logging.basicConfig(
    level=getattr(logging, config.log_level),
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class WebScraper:
    """
    A comprehensive web scraper class implementing best practices and scientific methods.
    
    This class provides functionality for:
    - Respectful web scraping with rate limiting
    - User agent rotation
    - Robots.txt compliance checking
    - Error handling and retry mechanisms
    - Data export in multiple formats
    - Dynamic content scraping with Selenium
    """
    
    def __init__(self, 
                 delay_range: Optional[tuple] = None,
                 timeout: Optional[int] = None,
                 max_retries: Optional[int] = None,
                 respect_robots: Optional[bool] = None,
                 use_selenium: Optional[bool] = None):
        """
        Initialize the web scraper with configuration parameters.
        
        Args:
            delay_range (tuple): Range of seconds to wait between requests (min, max)
            timeout (int): Request timeout in seconds
            max_retries (int): Maximum number of retry attempts for failed requests
            respect_robots (bool): Whether to check robots.txt before scraping
            use_selenium (bool): Whether to use Selenium for dynamic content
        """
        # Use provided parameters or fall back to config values
        self.delay_range = delay_range or config.delay_range
        self.timeout = timeout or config.timeout
        self.max_retries = max_retries or config.max_retries
        self.respect_robots = respect_robots if respect_robots is not None else config.respect_robots
        self.use_selenium = use_selenium if use_selenium is not None else config.use_selenium
        
        # Initialize session for connection pooling
        self.session = requests.Session()
        self.session.timeout = self.timeout
        
        # Set up proxies if configured
        proxy_dict = config.get_proxy_dict()
        if proxy_dict:
            self.session.proxies.update(proxy_dict)
            logger.info(f"Using proxies: {proxy_dict}")
        
        # Set up user agent rotation
        if USER_AGENT_AVAILABLE and not config.custom_user_agent:
            try:
                self.user_agent = UserAgent()
            except Exception as e:
                logger.warning(f"Failed to initialize UserAgent: {e}")
                self.user_agent = None
        else:
            self.user_agent = None
            
        # Default user agent fallback
        self.default_user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        
        # Initialize Selenium driver if needed
        self.driver = None
        if self.use_selenium:
            self._setup_selenium()
            
        # Track scraping statistics
        self.stats = {
            'requests_made': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'start_time': datetime.now()
        }
        
        logger.info("WebScraper initialized successfully")
        logger.debug(f"Configuration: {config.to_dict()}")
    
    def _setup_selenium(self):
        """Set up Selenium WebDriver with appropriate options."""
        try:
            chrome_options = Options()
            
            if config.selenium_headless:
                chrome_options.add_argument("--headless")  # Run in background
            
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument(f"--window-size={config.selenium_window_size}")
            
            # Add user agent
            user_agent = config.custom_user_agent or self._get_user_agent()
            chrome_options.add_argument(f"--user-agent={user_agent}")
            
            # Set Chrome driver path if specified
            if config.chrome_driver_path:
                os.environ['webdriver.chrome.driver'] = config.chrome_driver_path
            
            self.driver = webdriver.Chrome(options=chrome_options)
            logger.info("Selenium WebDriver initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Selenium WebDriver: {e}")
            self.use_selenium = False
    
    def _get_user_agent(self) -> str:
        """Get a random user agent for requests."""
        if config.custom_user_agent:
            return config.custom_user_agent
        
        if self.user_agent:
            try:
                return self.user_agent.random
            except Exception:
                return self.default_user_agent
        return self.default_user_agent
    
    def _check_robots_txt(self, url: str) -> bool:
        """
        Check if scraping is allowed according to robots.txt.
        
        Args:
            url (str): The URL to check
            
        Returns:
            bool: True if scraping is allowed, False otherwise
        """
        if not self.respect_robots:
            return True
            
        try:
            parsed_url = urlparse(url)
            robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
            
            rp = RobotFileParser()
            rp.set_url(robots_url)
            rp.read()
            
            can_fetch = rp.can_fetch(self._get_user_agent(), url)
            logger.info(f"Robots.txt check for {url}: {'Allowed' if can_fetch else 'Disallowed'}")
            return can_fetch
            
        except Exception as e:
            logger.warning(f"Could not check robots.txt for {url}: {e}")
            return True  # Default to allowed if we can't check
    
    def _make_request(self, url: str, method: str = 'GET', **kwargs) -> Optional[requests.Response]:
        """
        Make an HTTP request with proper error handling and retry logic.
        
        Args:
            url (str): The URL to request
            method (str): HTTP method (GET, POST, etc.)
            **kwargs: Additional arguments to pass to requests
            
        Returns:
            Optional[requests.Response]: Response object or None if failed
        """
        headers = kwargs.get('headers', {})
        headers['User-Agent'] = self._get_user_agent()
        kwargs['headers'] = headers
        
        for attempt in range(self.max_retries):
            try:
                self.stats['requests_made'] += 1
                
                if method.upper() == 'GET':
                    response = self.session.get(url, **kwargs)
                elif method.upper() == 'POST':
                    response = self.session.post(url, **kwargs)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                response.raise_for_status()
                self.stats['successful_requests'] += 1
                logger.info(f"Successful request to {url} (attempt {attempt + 1})")
                return response
                
            except requests.exceptions.RequestException as e:
                self.stats['failed_requests'] += 1
                logger.warning(f"Request failed to {url} (attempt {attempt + 1}): {e}")
                
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.info(f"Waiting {wait_time} seconds before retry...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"All {self.max_retries} attempts failed for {url}")
                    return None
        
        return None
    
    def _random_delay(self):
        """Add a random delay between requests to be respectful."""
        delay = random.uniform(*self.delay_range)
        logger.debug(f"Waiting {delay:.2f} seconds...")
        time.sleep(delay)
    
    def scrape_website(self, url: str, selectors: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Scrape data from a website using specified CSS selectors.
        
        Args:
            url (str): The URL to scrape
            selectors (Optional[Dict[str, str]]): CSS selectors for data extraction
                Format: {'field_name': 'css_selector'}
                
        Returns:
            Dict[str, Any]: Scraped data organized by field names
        """
        logger.info(f"Starting to scrape: {url}")
        
        # Check robots.txt
        if not self._check_robots_txt(url):
            logger.warning(f"Scraping disallowed by robots.txt for {url}")
            return {}
        
        # Get page content
        if self.use_selenium:
            content = self._get_content_selenium(url)
        else:
            content = self._get_content_requests(url)
        
        if not content:
            logger.error(f"Failed to get content from {url}")
            return {}
        
        # Parse HTML
        soup = BeautifulSoup(content, 'html.parser')
        
        # Extract data based on selectors
        data = {}
        if selectors:
            for field_name, selector in selectors.items():
                try:
                    elements = soup.select(selector)
                    if elements:
                        if len(elements) == 1:
                            data[field_name] = elements[0].get_text(strip=True)
                        else:
                            data[field_name] = [elem.get_text(strip=True) for elem in elements]
                    else:
                        data[field_name] = None
                        logger.warning(f"No elements found for selector '{selector}'")
                except Exception as e:
                    logger.error(f"Error extracting data for field '{field_name}': {e}")
                    data[field_name] = None
        
        # Add metadata
        data['_metadata'] = {
            'url': url,
            'scraped_at': datetime.now().isoformat(),
            'title': soup.title.string if soup.title else None,
            'status': 'success'
        }
        
        logger.info(f"Successfully scraped data from {url}")
        return data
    
    def _get_content_requests(self, url: str) -> Optional[str]:
        """Get page content using requests library."""
        response = self._make_request(url)
        if response:
            return response.text
        return None
    
    def _get_content_selenium(self, url: str) -> Optional[str]:
        """Get page content using Selenium for dynamic content."""
        if not self.driver:
            logger.error("Selenium driver not available")
            return None
        
        try:
            self.driver.get(url)
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Additional wait for dynamic content
            time.sleep(2)
            
            return self.driver.page_source
            
        except Exception as e:
            logger.error(f"Error getting content with Selenium: {e}")
            return None
    
    def export_to_csv(self, data: Union[Dict, List[Dict]], filename: str):
        """
        Export scraped data to CSV format.
        
        Args:
            data: Dictionary or list of dictionaries containing scraped data
            filename (str): Output filename
        """
        try:
            if isinstance(data, dict):
                # Single record
                data_list = [data]
            else:
                # Multiple records
                data_list = data
            
            # Remove metadata for CSV export
            clean_data = []
            for record in data_list:
                clean_record = {k: v for k, v in record.items() if not k.startswith('_')}
                clean_data.append(clean_record)
            
            if PANDAS_AVAILABLE:
                df = pd.DataFrame(clean_data)
                df.to_csv(filename, index=False)
            else:
                # Basic CSV export without pandas
                if clean_data:
                    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                        fieldnames = clean_data[0].keys()
                        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                        writer.writeheader()
                        writer.writerows(clean_data)
            
            logger.info(f"Data exported to {filename}")
            
        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")
    
    def export_to_json(self, data: Union[Dict, List[Dict]], filename: str):
        """
        Export scraped data to JSON format.
        
        Args:
            data: Dictionary or list of dictionaries containing scraped data
            filename (str): Output filename
        """
        try:
            with open(filename, 'w', encoding='utf-8') as jsonfile:
                json.dump(data, jsonfile, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"Data exported to {filename}")
            
        except Exception as e:
            logger.error(f"Error exporting to JSON: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get scraping statistics."""
        stats = self.stats.copy()
        stats['duration'] = (datetime.now() - stats['start_time']).total_seconds()
        stats['success_rate'] = (
            stats['successful_requests'] / stats['requests_made'] 
            if stats['requests_made'] > 0 else 0
        )
        return stats
    
    def close(self):
        """Clean up resources."""
        if self.driver:
            self.driver.quit()
            logger.info("Selenium WebDriver closed")
        
        self.session.close()
        logger.info("Session closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


# Example usage and testing
if __name__ == "__main__":
    # Example: Scrape a website using configuration
    with WebScraper() as scraper:
        # Use selectors from configuration
        selectors = config.selectors
        
        # Scrape data using URL from configuration
        data = scraper.scrape_website(
            config.target_url,
            selectors=selectors
        )
        
        # Export data using configured filenames
        scraper.export_to_json(data, config.output_json)
        scraper.export_to_csv([data], config.output_csv)
        
        # Print statistics
        print("Scraping Statistics:")
        for key, value in scraper.get_statistics().items():
            print(f"  {key}: {value}")
        
        print(f"\nData exported to:")
        print(f"  JSON: {config.output_json}")
        print(f"  CSV: {config.output_csv}") 