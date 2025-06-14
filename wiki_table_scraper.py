"""
Wikipedia Table Scraper

A simple script to scrape table data from Wikipedia pages.
This script extracts table data and saves it to CSV format.

Author: Web Scraper Project
Date: 2024
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
from config import config

def scrape_wikipedia_table(url=None, table_index=None):
    """
    Scrape table data from a Wikipedia page.
    
    Args:
        url (str, optional): The Wikipedia URL to scrape. If None, uses config.wiki_url.
        table_index (int, optional): Index of the table to scrape. If None, uses config.wiki_table_index.
    
    Returns:
        pandas.DataFrame: The scraped table data
    """
    # Use configuration values if not provided
    if url is None:
        url = config.wiki_url
    if table_index is None:
        table_index = config.wiki_table_index
    
    # Send an HTTP request to the webpage
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for bad status codes
    
    # Parse the HTML content
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Print the title of the webpage to verify
    print("Title: " + soup.title.text)
    
    # Find all tables and select the specified one
    tables = soup.find_all('table')
    if not tables:
        raise ValueError("No tables found on the page")
    
    if table_index >= len(tables):
        raise ValueError(f"Table index {table_index} out of range. Found {len(tables)} tables.")
    
    table = tables[table_index]
    
    # Extract table rows
    rows = table.find_all('tr')
    
    if not rows:
        raise ValueError("No rows found in the selected table")
    
    # Extract headers from the first row (using <th> tags)
    headers = [header.text.strip() for header in rows[0].find_all('th')]
    
    # If no headers found, try using the first row as headers
    if not headers:
        headers = [col.text.strip() for col in rows[0].find_all('td')]
        rows = rows[1:]  # Skip the first row since we used it as headers
    
    # Loop through the rows and extract data
    data = []
    for row in rows[1:] if headers else rows:  # Skip header row if headers were found
        cols = row.find_all('td')
        cols = [col.text.strip() for col in cols]
        if cols:  # Only add non-empty rows
            data.append(cols)
    
    # Convert the data into a pandas DataFrame
    df = pd.DataFrame(data, columns=headers)
    
    return df

def main():
    """Main function to demonstrate the scraper."""
    try:
        print(f"Scraping URL: {config.wiki_url}")
        print(f"Table index: {config.wiki_table_index}")
        print(f"Output file: {config.wiki_output_file}")
        
        # Scrape the table using configuration
        df = scrape_wikipedia_table()
        
        # Display the first few rows of the DataFrame
        print("\nFirst few rows of the scraped data:")
        print(df.head())
        
        # Save the DataFrame to a CSV file
        df.to_csv(config.wiki_output_file, index=False)
        print(f"\nData saved to {config.wiki_output_file}")
        
        # Print some statistics
        print(f"\nTable statistics:")
        print(f"Rows: {len(df)}")
        print(f"Columns: {len(df.columns)}")
        print(f"Columns: {list(df.columns)}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main() 