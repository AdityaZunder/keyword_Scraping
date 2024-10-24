#scraper.py
import requests
from bs4 import BeautifulSoup
import random

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
]

def scrape_url(url, keywords, proxy=None):
    headers = {
        "User-Agent": random.choice(USER_AGENTS)
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an error for bad responses
    except requests.exceptions.RequestException as err:
        print(f"Failed to retrieve HTML from {url}: {err}")
        return {"html": None, "tags": {keyword: [] for keyword in keywords}}

    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')

    # Store the HTML content and keyword counts
    tags_occurrences = {keyword: [] for keyword in keywords}

    # Extract tags where keywords occur
    for keyword in keywords:
        for tag in soup.find_all(True):
            if keyword.lower() in tag.text.lower():
                tags_occurrences[keyword].append(tag.name)

    return {"html": html_content, "tags": tags_occurrences}