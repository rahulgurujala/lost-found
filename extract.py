import asyncio
import concurrent.futures
import logging
import os
from functools import partial
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode

import aiohttp
import requests
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("lostfound_scraper")


class LostFoundScraper:
    """
    A scraper for lost and found items from Mumbai Police website.
    """

    def __init__(self, base_url: str, headers: Optional[Dict[str, str]] = None):
        """
        Initialize the scraper with base URL and optional headers.

        Args:
            base_url: The base URL for the scraper
            headers: Optional HTTP headers for requests
        """
        self.base_url = base_url
        self.headers = headers or {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) \
                AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari\
                    /537.36"
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def build_url(self, params: Dict[str, Any]) -> str:
        """
        Build a URL with the given parameters.

        Args:
            params: Dictionary of URL parameters

        Returns:
            Complete URL with parameters
        """
        return f"{self.base_url}?{urlencode(params)}"

    def fetch_page(self, url: str) -> Optional[str]:
        """
        Fetch the HTML content of a page.

        Args:
            url: URL to fetch

        Returns:
            HTML content as string or None if request failed
        """
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logger.error(f"Error fetching page {url}: {e}")
            return None

    def parse_html(self, html: str) -> BeautifulSoup:
        """
        Parse HTML content using BeautifulSoup.

        Args:
            html: HTML content as string

        Returns:
            BeautifulSoup object
        """
        return BeautifulSoup(html, "lxml")

    def extract_items(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """
        Extract lost/found items from the parsed HTML.

        Args:
            soup: BeautifulSoup object of the parsed HTML

        Returns:
            List of dictionaries containing item details
        """
        main_data = []

        # Fields to extract
        fields = [
            "Police Station",
            "Full Name",
            "Contact Number",
            "Address",
            "Pin code",
            "E-mail ID",
            "Date & Time",
            "Place of Lost / Found and Other Details (If Any)",
            "Article Description",
        ]

        # Process each table (one table per record)
        tables = soup.find_all("table", class_="mb-50")
        for table in tables:
            data = {}
            # Get all <p> tags within the table
            paragraphs = table.find_all("p")
            for p in paragraphs:
                # Get the label (title) and value spans
                label_span = p.find("span", {"title": True})
                value_span = p.find(
                    "span", class_=lambda x: x != "txt-val"
                )  # Exclude the label span
                if label_span and value_span:
                    field = label_span["title"]
                    if field in fields:
                        data[field] = value_span.text.strip()

            # Append only if we have some data
            # if data:
            main_data.append(data)

        return main_data

    def get_total_pages(self, soup: BeautifulSoup) -> int:
        """
        Extract the total number of pages from pagination.

        Args:
            soup: BeautifulSoup object of the parsed HTML

        Returns:
            Total number of pages, defaults to 1 if not found
        """
        pagination = soup.find("ul", class_="pagination")
        if not pagination:
            return 1

        # Try to find the last page number
        page_links = pagination.find_all("a")
        max_page = 1

        for link in page_links:
            try:
                page_num = int(link.text.strip())
                max_page = max(max_page, page_num)
            except (ValueError, TypeError):
                continue

        return max_page

    async def fetch_page_async(
        self, url: str, session: aiohttp.ClientSession
    ) -> Optional[str]:
        """
        Fetch the HTML content of a page asynchronously.

        Args:
            url: URL to fetch
            session: aiohttp ClientSession

        Returns:
            HTML content as string or None if request failed
        """
        try:
            async with session.get(url, timeout=30) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    logger.error(f"Error fetching page {url}: HTTP {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error fetching page {url}: {e}")
            return None

    async def scrape_page_async(
        self, page: int, params: Dict[str, Any], session: aiohttp.ClientSession
    ) -> List[Dict[str, str]]:
        """
        Scrape a single page asynchronously.

        Args:
            page: Page number to scrape
            params: Dictionary of URL parameters
            session: aiohttp ClientSession

        Returns:
            List of dictionaries containing item details
        """
        page_params = params.copy()
        page_params["page"] = str(page)
        page_url = f"{self.base_url}?{self._build_query_string(page_params)}"

        html = await self.fetch_page_async(page_url, session)
        if not html:
            return []

        soup = self.parse_html(html)
        return self.extract_items(soup)

    async def scrape_all_pages_async(
        self, params: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """
        Scrape all pages for the given parameters asynchronously.

        Args:
            params: Dictionary of URL parameters

        Returns:
            List of all items from all pages
        """
        all_items = []

        # Create aiohttp session
        async with aiohttp.ClientSession(headers=self.headers) as session:
            # Get the first page
            first_page_params = params.copy()
            first_page_params["page"] = "1"
            url = f"{self.base_url}?{self._build_query_string(first_page_params)}"

            html = await self.fetch_page_async(url, session)
            if not html:
                return all_items

            soup = self.parse_html(html)
            items = self.extract_items(soup)
            all_items.extend(items)

            # Get total pages
            total_pages = self.get_total_pages(soup)
            logger.info(f"Found {total_pages} pages to scrape")

            # Scrape remaining pages concurrently
            if total_pages > 1:
                tasks = []
                for page in range(2, total_pages + 1):
                    task = self.scrape_page_async(page, params, session)
                    tasks.append(task)

                # Wait for all tasks to complete
                results = await asyncio.gather(*tasks)

                # Extend all_items with results
                for page_items in results:
                    all_items.extend(page_items)

        return all_items

    def scrape_all_pages_parallel(
        self, params: Dict[str, Any], max_workers: int = 5
    ) -> List[Dict[str, str]]:
        """
        Scrape all pages for the given parameters in parallel using \
            ThreadPoolExecutor.

        Args:
            params: Dictionary of URL parameters
            max_workers: Maximum number of worker threads

        Returns:
            List of all items from all pages
        """
        all_items = []

        # Get the first page
        first_page_params = params.copy()
        first_page_params["page"] = 1
        url = self.build_url(first_page_params)

        html = self.fetch_page(url)
        if not html:
            return all_items

        soup = self.parse_html(html)
        items = self.extract_items(soup)
        all_items.extend(items)

        # Get total pages
        total_pages = self.get_total_pages(soup)
        logger.info(f"Found {total_pages} pages to scrape")

        # Scrape remaining pages in parallel
        if total_pages > 1:
            with concurrent.futures.ThreadPoolExecutor(
                max_workers=max_workers
            ) as executor:
                # Create a partial function with params
                scrape_page_func = partial(self._scrape_single_page, params=params)

                # Submit tasks for each page
                future_to_page = {
                    executor.submit(scrape_page_func, page): page
                    for page in range(2, total_pages + 1)
                }

                # Process results as they complete
                for future in concurrent.futures.as_completed(future_to_page):
                    page = future_to_page[future]
                    try:
                        page_items = future.result()
                        all_items.extend(page_items)
                        logger.info(f"Completed page {page}/{total_pages}")
                    except Exception as e:
                        logger.error(f"Error processing page {page}: {e}")

        return all_items

    def _scrape_single_page(
        self, page: int, params: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """
        Helper method to scrape a single page for parallel processing.

        Args:
            page: Page number to scrape
            params: Dictionary of URL parameters

        Returns:
            List of dictionaries containing item details
        """
        page_params = params.copy()
        page_params["page"] = page
        page_url = self.build_url(page_params)

        html = self.fetch_page(page_url)
        if not html:
            return []

        soup = self.parse_html(html)
        return self.extract_items(soup)

    def _build_query_string(self, params: Dict[str, Any]) -> str:
        """
        Build a query string from parameters.

        Args:
            params: Dictionary of URL parameters

        Returns:
            URL-encoded query string
        """
        return urlencode(params)


def create_scraper(base_url: str) -> LostFoundScraper:
    """
    Factory function to create a scraper instance.

    Args:
        base_url: The base URL for the scraper

    Returns:
        Configured LostFoundScraper instance
    """
    return LostFoundScraper(base_url)


# Update the save_to_csv function
def save_to_csv(items: List[Dict[str, str]], filename: str) -> bool:
    """
    Save scraped items to a CSV file.

    Args:
        items: List of dictionaries containing item details
        filename: Path to save the CSV file

    Returns:
        True if successful, False otherwise
    """
    import csv

    from tqdm import tqdm

    if not items:
        logger.warning("No items to save")
        return False

    try:
        with open(filename, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = items[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for item in tqdm(items, desc="Saving to CSV", unit="item"):
                writer.writerow(item)

        logger.info(f"Saved {len(items)} items to {filename}")
        return True
    except Exception as e:
        logger.error(f"Error saving to CSV: {e}")
        return False


# Update the save_to_json function
def save_to_json(items: List[Dict[str, str]], filename: str) -> bool:
    """
    Save scraped items to a JSON file.

    Args:
        items: List of dictionaries containing item details
        filename: Path to save the JSON file

    Returns:
        True if successful, False otherwise
    """
    import json

    from tqdm import tqdm

    if not items:
        logger.warning("No items to save")
        return False

    try:
        # Process items with progress bar
        processed_items = []
        for item in tqdm(items, desc="Processing for JSON", unit="item"):
            processed_items.append(item)

        with open(filename, "w", encoding="utf-8") as jsonfile:
            json.dump(processed_items, jsonfile, indent=2, ensure_ascii=False)

        logger.info(f"Saved {len(items)} items to {filename}")
        return True
    except Exception as e:
        logger.error(f"Error saving to JSON: {e}")
        return False


def extract_details_from_html_file(file_path: str) -> List[Dict[str, str]]:
    """
    Utility function to extract details from a local HTML file.

    Args:
        file_path: Path to the HTML file

    Returns:
        List of dictionaries containing the extracted details
    """
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return []

    # Create a scraper instance
    scraper = create_scraper("dummy_url")

    # Extract details
    return scraper.extract_details_from_file(file_path)
