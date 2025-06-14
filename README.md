# Web Scraper Project

A comprehensive web scraping solution built with Python, following best practices and scientific methods.

## Features

- **Robust HTTP requests** with proper error handling and retry mechanisms
- **BeautifulSoup4** for HTML parsing and data extraction
- **Selenium** for dynamic content scraping (optional)
- **Data export** to CSV and JSON formats with metadata
- **Rate limiting** and respectful scraping practices
- **User agent rotation** to avoid detection
- **Environment variable** configuration management
- **Configuration-driven** scraping with flexible settings
- **Robots.txt compliance** checking
- **Proxy support** for HTTP and HTTPS
- **Comprehensive logging** and statistics tracking
- **Context manager** support for resource management
- **Wikipedia table scraper** for specialized table data extraction
- **Unified configuration** across all scraper components

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- A code editor (VS Code, PyCharm, Jupyter Notebooks, etc.)
- Basic understanding of HTML structure
- Chrome/Chromium browser (if using Selenium)

## Installation

1. Clone or download this repository
2. Navigate to the project directory
3. Install dependencies:

```bash
pip install -r requirements.txt
```

## How to Run the Project

To run the web scraper locally, follow these steps:

1. **Set up configuration** (optional but recommended):

   ```bash
   # Copy the environment template
   cp .env.example .env

   # Edit .env file with your settings
   nano .env  # or use your preferred editor
   ```

2. **Run the main scraper script**:

   ```bash
   python web_scraper.py
   ```

   This will execute the example code in `web_scraper.py`, scrape a sample website, and export the results to `scraped_data.json` and `scraped_data.csv`.

**Note:**

- If you see a warning about urllib3/LibreSSL, this is a compatibility warning that doesn't prevent the scraper from running
- The scraper uses default configuration if no `.env` file is present
- You can customize the scraping target and selectors by editing the `.env` file

## Usage

### Basic Usage

```python
from web_scraper import WebScraper

# Initialize scraper with default configuration
scraper = WebScraper()

# Scrape a website
data = scraper.scrape_website("https://example.com")

# Export data
scraper.export_to_csv(data, "output.csv")
```

### Wikipedia Table Scraping

```python
from wiki_table_scraper import scrape_wikipedia_table

# Scrape Wikipedia table using configuration
df = scrape_wikipedia_table()

# Or specify custom parameters
df = scrape_wikipedia_table(
    url="https://en.wikipedia.org/wiki/Your_page",
    table_index=1  # Second table on the page
)

# Save to CSV
df.to_csv("my_table_data.csv", index=False)
```

### Advanced Usage with Custom Configuration

```python
from web_scraper import WebScraper

# Initialize scraper with custom settings
scraper = WebScraper(
    delay_range=(1, 3),
    timeout=60,
    max_retries=5,
    respect_robots=False,
    use_selenium=True
)

# Define custom selectors
selectors = {
    'title': 'h1.product-title',
    'price': '.price-value',
    'description': '.product-description',
    'images': 'img.product-image'
}

# Scrape data
data = scraper.scrape_website(
    "https://example.com/product",
    selectors=selectors
)

# Export in multiple formats
scraper.export_to_json(data, "product_data.json")
scraper.export_to_csv([data], "product_data.csv")

# Get scraping statistics
stats = scraper.get_statistics()
print(f"Success rate: {stats['success_rate']:.2%}")
```

### Using Configuration Files

The scraper automatically loads settings from environment variables. Create a `.env` file:

```env
# Main scraper settings
TARGET_URL=https://example.com
SELECTORS={"title": "h1", "price": ".price", "description": ".desc"}
DELAY_MIN=2
DELAY_MAX=4
OUTPUT_JSON=my_data.json
OUTPUT_CSV=my_data.csv

# Wikipedia scraper settings
WIKI_URL=https://en.wikipedia.org/wiki/Your_page
WIKI_TABLE_INDEX=0
WIKI_OUTPUT_FILE=wiki_data.csv
```

### Context Manager Usage (Recommended)

```python
from web_scraper import WebScraper

# Use context manager for automatic resource cleanup
with WebScraper() as scraper:
    data = scraper.scrape_website("https://example.com")
    scraper.export_to_json(data, "output.json")
    print(scraper.get_statistics())
```

## Project Structure

```
web-scraper/
├── web_scraper.py          # Main scraper class with all functionality
├── wiki_table_scraper.py   # Wikipedia table scraper
├── config.py               # Configuration management module
├── requirements.txt        # Python dependencies
├── .gitignore             # Git ignore rules
├── README.md              # This documentation
├── .env.example           # Environment variables template
└── .env                   # Environment variables (create from template)
```

## Configuration Management

This project uses environment variables for configuration management, following best practices for security and flexibility.

### Environment Variables Setup

1. **Create a `.env` file** in the project root:

```bash
cp .env.example .env
```

2. **Edit the `.env` file** with your specific settings:

```env
# Target URL to scrape
TARGET_URL=https://example.com

# CSS Selectors for data extraction (JSON format)
SELECTORS={"title": "h1", "description": "p.description", "links": "a[href]"}

# Scraping behavior settings
DELAY_MIN=2
DELAY_MAX=4
TIMEOUT=30
MAX_RETRIES=3
RESPECT_ROBOTS=true
USE_SELENIUM=false

# Output settings
OUTPUT_JSON=my_data.json
OUTPUT_CSV=my_data.csv

# User agent settings (optional)
CUSTOM_USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36

# Proxy settings (optional)
HTTP_PROXY=http://proxy.example.com:8080
HTTPS_PROXY=https://proxy.example.com:8080

# Selenium settings (if using Selenium)
CHROME_DRIVER_PATH=/path/to/chromedriver
SELENIUM_HEADLESS=true
SELENIUM_WINDOW_SIZE=1920,1080

# Logging settings
LOG_LEVEL=INFO
LOG_FILE=scraper.log

# Wikipedia settings
WIKI_URL=https://en.wikipedia.org/wiki/Your_page
WIKI_TABLE_INDEX=0
WIKI_OUTPUT_FILE=wiki_data.csv
```

### Configuration Options

| Variable               | Description                              | Default                    | Example                              |
| ---------------------- | ---------------------------------------- | -------------------------- | ------------------------------------ |
| `TARGET_URL`           | URL to scrape                            | `https://httpbin.org/html` | `https://example.com`                |
| `SELECTORS`            | CSS selectors in JSON format             | `{"title": "h1"}`          | `{"title": "h1", "price": ".price"}` |
| `DELAY_MIN`            | Minimum delay between requests (seconds) | `2`                        | `1`                                  |
| `DELAY_MAX`            | Maximum delay between requests (seconds) | `4`                        | `3`                                  |
| `TIMEOUT`              | Request timeout (seconds)                | `30`                       | `60`                                 |
| `MAX_RETRIES`          | Maximum retry attempts                   | `3`                        | `5`                                  |
| `RESPECT_ROBOTS`       | Check robots.txt                         | `true`                     | `false`                              |
| `USE_SELENIUM`         | Use Selenium for dynamic content         | `false`                    | `true`                               |
| `OUTPUT_JSON`          | JSON output filename                     | `scraped_data.json`        | `my_data.json`                       |
| `OUTPUT_CSV`           | CSV output filename                      | `scraped_data.csv`         | `my_data.csv`                        |
| `CUSTOM_USER_AGENT`    | Custom user agent string                 | Auto-generated             | Custom string                        |
| `HTTP_PROXY`           | HTTP proxy URL                           | None                       | `http://proxy:8080`                  |
| `HTTPS_PROXY`          | HTTPS proxy URL                          | None                       | `https://proxy:8080`                 |
| `CHROME_DRIVER_PATH`   | Path to ChromeDriver                     | Auto-detect                | `/usr/bin/chromedriver`              |
| `SELENIUM_HEADLESS`    | Run Selenium in headless mode            | `true`                     | `false`                              |
| `SELENIUM_WINDOW_SIZE` | Selenium window size                     | `1920,1080`                | `1366,768`                           |
| `LOG_LEVEL`            | Logging level                            | `INFO`                     | `DEBUG`                              |
| `LOG_FILE`             | Log file path                            | `scraper.log`              | `my_scraper.log`                     |
| `WIKI_URL`             | Wikipedia URL to scrape                  | Cloud computing comparison | `https://en.wikipedia.org/wiki/...`  |
| `WIKI_TABLE_INDEX`     | Table index to scrape                    | `0`                        | `1`                                  |
| `WIKI_OUTPUT_FILE`     | Wikipedia output filename                | `wikipedia_table_data.csv` | `my_wiki_data.csv`                   |

### Benefits of Environment Variables

1. **Security**: Sensitive information (proxies, API keys) is not hardcoded
2. **Flexibility**: Easy to change settings without modifying code
3. **Environment-specific**: Different settings for development, testing, production
4. **Version Control**: `.env` files can be excluded from git (add to `.gitignore`)
5. **Best Practices**: Follows industry standards for configuration management

### Using Configuration in Code

The scraper automatically uses environment variables, but you can also override them programmatically:

```python
from web_scraper import WebScraper

# Use default configuration from .env
scraper = WebScraper()

# Override specific settings
scraper = WebScraper(
    delay_range=(1, 2),
    timeout=60,
    respect_robots=False
)
```

## API Reference

### WebScraper Class

#### Constructor Parameters

- `delay_range` (tuple): Range of seconds to wait between requests (min, max)
- `timeout` (int): Request timeout in seconds
- `max_retries` (int): Maximum number of retry attempts for failed requests
- `respect_robots` (bool): Whether to check robots.txt before scraping
- `use_selenium` (bool): Whether to use Selenium for dynamic content

#### Methods

- `scrape_website(url, selectors=None)`: Scrape data from a website
- `export_to_csv(data, filename)`: Export data to CSV format
- `export_to_json(data, filename)`: Export data to JSON format
- `get_statistics()`: Get scraping statistics
- `close()`: Clean up resources

#### Context Manager

The class supports context manager protocol for automatic resource cleanup:

```python
with WebScraper() as scraper:
    # Your scraping code here
    pass  # Resources automatically cleaned up
```

### Wikipedia Table Scraper

#### Functions

- `scrape_wikipedia_table(url=None, table_index=None)`: Scrape table data from Wikipedia pages

#### Parameters

- `url` (str, optional): Wikipedia URL to scrape. Uses `config.wiki_url` if not provided
- `table_index` (int, optional): Index of table to scrape. Uses `config.wiki_table_index` if not provided

#### Returns

- `pandas.DataFrame`: The scraped table data

### Configuration Management

All configuration is managed through the `config` module, which provides:

- **Unified access**: All settings accessible via `config.variable_name`
- **Environment variable loading**: Automatic loading from `.env` files
- **Default values**: Sensible defaults for all settings
- **Type conversion**: Automatic conversion of string values to appropriate types
- **Validation**: Basic validation and error handling

## Best Practices

1. **Respect robots.txt** - Always check website's robots.txt file
2. **Rate limiting** - Add delays between requests
3. **User agent rotation** - Use different user agents
4. **Error handling** - Implement proper exception handling
5. **Data validation** - Validate scraped data
6. **Legal compliance** - Ensure compliance with website terms of service
7. **Configuration management** - Use environment variables for settings
8. **Logging** - Implement comprehensive logging for debugging
9. **Resource management** - Use context managers for automatic cleanup
10. **Proxy usage** - Use proxies when scraping large amounts of data

## License

This project is for educational purposes. Always respect website terms of service and legal requirements when scraping.
