import requests
from bs4 import BeautifulSoup
import random
import time
import os
from dotenv import load_dotenv

# Load the .env file
load_dotenv(dotenv_path='config.env')  # Make sure to specify the correct path

# Read delay values from .env
DELAY_MIN = float(os.getenv("DELAY_MIN", 5))  # Default to 5 seconds
DELAY_MAX = float(os.getenv("DELAY_MAX", 10))  # Default to 10 seconds
N = int(os.getenv("N", 10))  # Default to 10 if not found

# List of User-Agent headers
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"
]

def google_search(keywords, region='IN'):
    query = '+'.join(keywords)
    url = f"https://www.google.com/search?q={query}&gl={region}"
    
    headers = {
        "User-Agent": random.choice(USER_AGENTS)  # Randomize User-Agent
    }

    # Adding a delay to avoid rate limiting (from .env file)
    time.sleep(random.uniform(DELAY_MIN, DELAY_MAX))

    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Failed to retrieve search results: {response.status_code}")
            return []
    except requests.exceptions.RequestException as e:
        print(f"Error occurred: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    results = []
    for g in soup.find_all('div', class_='g'):
        link = g.find('a')
        if link:
            results.append(link['href'])
    
    return results[:N]  # Return the top N results based on the environment variable

# Example usage
if __name__ == "__main__":
    keywords = ['example', 'keyword']  # Replace with actual keywords
    print(google_search(keywords))