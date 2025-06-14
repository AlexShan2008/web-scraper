"""
Configuration module for web scraper settings.

This module manages all configuration settings for the web scraper,
loading them from environment variables with sensible defaults.
"""

import os
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration class for web scraper settings."""
    
    def __init__(self):
        """Initialize configuration with values from environment variables."""
        self.target_url = os.getenv('TARGET_URL', 'https://httpbin.org/html')
        self.selectors = self._parse_selectors()
        self.delay_range = (
            float(os.getenv('DELAY_MIN', 2)),
            float(os.getenv('DELAY_MAX', 4))
        )
        self.timeout = int(os.getenv('TIMEOUT', 30))
        self.max_retries = int(os.getenv('MAX_RETRIES', 3))
        self.respect_robots = os.getenv('RESPECT_ROBOTS', 'true').lower() == 'true'
        self.use_selenium = os.getenv('USE_SELENIUM', 'false').lower() == 'true'
        
        # Output settings
        self.output_json = os.getenv('OUTPUT_JSON', 'scraped_data.json')
        self.output_csv = os.getenv('OUTPUT_CSV', 'scraped_data.csv')
        
        # User agent settings
        self.custom_user_agent = os.getenv('CUSTOM_USER_AGENT')
        
        # Proxy settings
        self.http_proxy = os.getenv('HTTP_PROXY')
        self.https_proxy = os.getenv('HTTPS_PROXY')
        
        # Selenium settings
        self.chrome_driver_path = os.getenv('CHROME_DRIVER_PATH')
        self.selenium_headless = os.getenv('SELENIUM_HEADLESS', 'true').lower() == 'true'
        self.selenium_window_size = os.getenv('SELENIUM_WINDOW_SIZE', '1920,1080')
        
        # Logging settings
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        self.log_file = os.getenv('LOG_FILE', 'scraper.log')
    
    def _parse_selectors(self) -> Dict[str, str]:
        """Parse CSS selectors from environment variable."""
        selectors_str = os.getenv('SELECTORS', '{}')
        try:
            return json.loads(selectors_str)
        except json.JSONDecodeError:
            # Default selectors if parsing fails
            return {
                'title': 'h1',
                'description': 'meta[name="description"]',
                'links': 'a[href]'
            }
    
    def get_proxy_dict(self) -> Optional[Dict[str, str]]:
        """Get proxy configuration as dictionary for requests."""
        proxies = {}
        if self.http_proxy:
            proxies['http'] = self.http_proxy
        if self.https_proxy:
            proxies['https'] = self.https_proxy
        return proxies if proxies else None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary for logging/debugging."""
        return {
            'target_url': self.target_url,
            'selectors': self.selectors,
            'delay_range': self.delay_range,
            'timeout': self.timeout,
            'max_retries': self.max_retries,
            'respect_robots': self.respect_robots,
            'use_selenium': self.use_selenium,
            'output_json': self.output_json,
            'output_csv': self.output_csv,
            'custom_user_agent': self.custom_user_agent,
            'http_proxy': self.http_proxy,
            'https_proxy': self.https_proxy,
            'chrome_driver_path': self.chrome_driver_path,
            'selenium_headless': self.selenium_headless,
            'selenium_window_size': self.selenium_window_size,
            'log_level': self.log_level,
            'log_file': self.log_file
        }


# Global configuration instance
config = Config() 