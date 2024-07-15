import requests
import logging

logger = logging.getLogger(__name__)


def fetch_url(url, params=None):
    """Utility function to fetch data from the given URL."""
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response
    except requests.RequestException as e:
        logger.error(f"Request failed for {url}: {e}")
        return None
