# abm/scraper.py
import requests
from bs4 import BeautifulSoup
import logging

# Configure logging for this module
logger = logging.getLogger(__name__)
# Ensure basic config is set somewhere (e.g., in dashboard.py or main entry point)
# logging.basicConfig(level=logging.INFO) # If running this file standalone for testing

def scrape_summary_for_domain(domain: str) -> str:
    """
    Attempts to scrape a basic summary (title or meta description)
    from the domain's homepage using requests and BeautifulSoup.
    Returns the summary string or an error message.
    """
    if not domain:
        logger.warning("Scrape attempt failed: No domain provided.")
        return "No domain provided for scraping."

    # Prepend protocol if missing - common mistake
    if not domain.startswith(('http://', 'https://')):
        url = f"https://{domain}"
    else:
        url = domain # Assume user provided full URL if protocol exists

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive'
    }
    logger.info(f"Attempting to scrape summary from URL: {url}")

    try:
        # Send GET request, allow redirects, set timeout
        response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        # Raise an exception for bad status codes (4xx or 5xx)
        response.raise_for_status()

        # Check if content type is HTML before parsing
        content_type = response.headers.get('Content-Type', '').lower()
        if 'text/html' not in content_type:
            logger.warning(f"Non-HTML content type received from {url}: {content_type}")
            return f"Could not scrape {domain}: Received non-HTML content ({content_type})."

        # Parse the HTML content using lxml
        soup = BeautifulSoup(response.content, 'lxml')

        # 1. Try to find the meta description tag
        meta_desc_tag = soup.find('meta', attrs={'name': 'description'})
        if meta_desc_tag and meta_desc_tag.get('content'):
            summary = meta_desc_tag['content'].strip()
            logger.info(f"Successfully scraped meta description for {domain}")
            return summary

        # 2. If no meta description, fallback to the title tag
        title_tag = soup.find('title')
        if title_tag and title_tag.string:
            summary = title_tag.string.strip()
            logger.info(f"No meta description found, scraped title tag for {domain}")
            return summary

        # 3. If neither found
        logger.warning(f"Could not find a suitable meta description or title tag for {domain}")
        return f"No standard summary (title/description) found via basic scraping for {domain}."

    except requests.exceptions.Timeout:
        logger.error(f"Timeout error while scraping {url}")
        return f"Scraping timed out for {domain}."
    except requests.exceptions.ConnectionError:
        logger.error(f"Connection error while scraping {url}")
        return f"Could not connect to {domain}."
    except requests.exceptions.HTTPError as http_err:
        logger.error(f"HTTP error occurred while scraping {url}: {http_err}")
        return f"HTTP Error {http_err.response.status_code} when accessing {domain}."
    except requests.exceptions.RequestException as req_err:
        # Catch other requests-related errors (e.g., TooManyRedirects)
        logger.error(f"Request error occurred while scraping {url}: {req_err}", exc_info=True)
        return f"Request error while scraping {domain}: {req_err.__class__.__name__}."
    except Exception as e:
        # Catch any other unexpected errors during parsing or processing
        logger.error(f"An unexpected error occurred during scraping {url}: {e}", exc_info=True)
        return f"An unexpected error occurred during scraping for {domain}."