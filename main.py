import random
import time
from google_search import google_search
from scraper import scrape_url
import pandas as pd
import os
from dotenv import load_dotenv
from urllib.parse import urlparse
from collections import Counter

# Load the config.env file
load_dotenv(dotenv_path='config.env')

# Read values from .env
N = int(os.getenv("N", 10))
DELAY_MIN = float(os.getenv("DELAY_MIN", 5))
DELAY_MAX = float(os.getenv("DELAY_MAX", 10))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", 3))

def normalize_url(url):
    parsed_url = urlparse(url)
    return f"{parsed_url.scheme}://{parsed_url.netloc}".lower()

def get_keywords_from_file(file_path):
    with open(file_path, 'r') as f:
        return [line.strip() for line in f if line.strip()]

def ensure_n_valid_urls(keywords, required_count=N):
    all_urls = google_search(keywords)
    valid_urls = []
    visited_urls = set()
    failed_urls = set()

    while len(valid_urls) < required_count and all_urls:
        for url in all_urls:
            normalized_url = normalize_url(url)

            if normalized_url in visited_urls or normalized_url in failed_urls:
                continue

            for attempt in range(MAX_RETRIES):
                occurrences = scrape_url(url, keywords)

                if occurrences['html'] is not None:
                    valid_urls.append(url)
                    visited_urls.add(normalized_url)
                    break
                else:
                    error_code = occurrences.get('error_code')
                    print(f"Attempt {attempt + 1} for {url}: Error {error_code if error_code else 'Unknown error'}")
                    if error_code in [403, 429]:  # Handle specific error codes
                        time.sleep(DELAY_MIN * (2 ** attempt))  # Exponential backoff
                    else:
                        failed_urls.add(normalized_url)
                        break

            if len(valid_urls) == required_count:
                break

        if len(valid_urls) < required_count:
            print("Fetching more URLs...")
            all_urls = google_search(keywords)
            time.sleep(random.uniform(DELAY_MIN, DELAY_MAX))

    return valid_urls[:required_count]

def find_common_words(keywords):
    """Find words common to at least 10 keywords."""
    word_counter = Counter()
    for keyword in keywords:
        for word in keyword.split():
            word_counter[word] += 1
    return [word for word, count in word_counter.items() if count >= 10]

if __name__ == "__main__":
    keywords = get_keywords_from_file('keywords.txt')
    valid_urls = ensure_n_valid_urls(keywords)

    # Find common words in at least 10 keywords
    common_words = find_common_words(keywords)

    # Initial DataFrame setup
    combined_df = pd.DataFrame(columns=["URL", "HTML"] + keywords + [f"{keyword} Count" for keyword in keywords] + common_words)

    for url in valid_urls:
        occurrences = scrape_url(url, keywords)

        row_data = {"URL": url, "HTML": occurrences['html']}

        # Populate keyword-related columns
        for keyword in keywords:
            row_data[keyword] = occurrences['tags'][keyword] if keyword in occurrences['tags'] else []
            row_data[f"{keyword} Count"] = occurrences['html'].lower().count(keyword.lower())

        # Populate common words count
        for word in common_words:
            row_data[word] = occurrences['html'].lower().count(word.lower())

        combined_df = pd.concat([combined_df, pd.DataFrame([row_data])], ignore_index=True)

    # Replace 'No occurrences' with 0
    combined_df.replace("No occurrences", 0, inplace=True)

    # Replace empty lists with 0
    combined_df = combined_df.applymap(lambda x: 0 if x == [] else x)

    # Drop columns where all values are either 0
    combined_df = combined_df.loc[:, (combined_df != 0).any(axis=0)]  # Drop columns where all values are 0

    combined_df.to_csv('combined_output.csv', index=False)
    print("Data saved to 'combined_output.csv'")
    keywords = get_keywords_from_file('keywords.txt')
    valid_urls = ensure_n_valid_urls(keywords)

    # Find common words in at least 10 keywords
    common_words = find_common_words(keywords)

    # Initial DataFrame setup
    combined_df = pd.DataFrame(columns=["URL", "HTML"] + keywords + [f"{keyword} Count" for keyword in keywords] + common_words)

    for url in valid_urls:
        occurrences = scrape_url(url, keywords)

        row_data = {"URL": url, "HTML": occurrences['html']}

        # Populate keyword-related columns
        for keyword in keywords:
            row_data[keyword] = occurrences['tags'][keyword] if keyword in occurrences['tags'] else []
            row_data[f"{keyword} Count"] = occurrences['html'].lower().count(keyword.lower())

        # Populate common words count
        for word in common_words:
            row_data[word] = occurrences['html'].lower().count(word.lower())

        combined_df = pd.concat([combined_df, pd.DataFrame([row_data])], ignore_index=True)

    # Replace 'No occurrences' and empty lists with 0, and then drop columns where all values are 0 or empty lists
    combined_df.replace(["No occurrences", []], 0, inplace=True)
    combined_df.dropna(axis=1, how='all', inplace=True)  # Drop columns with all NaN or empty lists replaced by 0
    combined_df = combined_df.loc[:, (combined_df != 0).any(axis=0)]  # Drop columns where all values are 0 or empty lists

    combined_df.to_csv('combined_output.csv', index=False)
    print("Data saved to 'combined_output.csv'")