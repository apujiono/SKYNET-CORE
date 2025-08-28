import requests
from bs4 import BeautifulSoup
import logging
import time

logger = logging.getLogger("Skynet")

def scrape_expired_domains(limit=20, config=None):
    """Scrape domain kadaluarsa dari ExpiredDomains.net dan sumber lain."""
    try:
        headers = {"User-Agent": config["user_agents"][0]}
        response = requests.get(config["scrape_url"], headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        domains = []
        for row in soup.select("table.base1 tbody tr")[:limit]:
            domain = row.select_one("td a").text
            domains.append(domain)
            time.sleep(2)  # Hindari rate limit
        logger.info(f"Scraped {len(domains)} expired domains.")
        return domains
    except Exception as e:
        logger.error(f"Scraping error: {e}")
        return []