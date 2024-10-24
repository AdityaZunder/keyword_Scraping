from google_search import google_search
from scraper import scrape_url
import pandas as pd

def get_keywords():
    keywords = input("Enter keywords separated by commas: ")
    return [keyword.strip() for keyword in keywords.split(',')]

def ensure_ten_valid_urls(keywords, required_count=10):
    all_urls = google_search(keywords)
    valid_urls = []

    while len(valid_urls) < required_count and all_urls:
        for url in all_urls:
            occurrences = scrape_url(url, keywords)
            if occurrences['html'] is not None:
                valid_urls.append(url)
                if len(valid_urls) == required_count:
                    break
        if len(valid_urls) < required_count:
            print("Fetching more URLs...")
            all_urls = google_search(keywords)  # Fetch more URLs if needed
    
    return valid_urls[:required_count]  # Ensure exactly 10 URLs are returned

if __name__ == "__main__":
    keywords = get_keywords()

    # Get a list of 10 valid URLs after filtering failed ones
    valid_urls = ensure_ten_valid_urls(keywords)

    # DataFrame to store URL, HTML, and keyword occurrences
    combined_df = pd.DataFrame(columns=["URL", "HTML"] + keywords)

    for url in valid_urls:
        occurrences = scrape_url(url, keywords)

        # Prepare a row to insert into the DataFrame
        row_data = {"URL": url, "HTML": occurrences['html']}

        # Store unique tags for each keyword (no repetitions)
        for keyword in keywords:
            unique_tags = list(set(occurrences['tags'][keyword]))  # Remove duplicate tags
            row_data[keyword] = ', '.join(unique_tags) if unique_tags else "No occurrences"

        # Create a DataFrame for the current row and concatenate it with combined_df
        combined_df = pd.concat([combined_df, pd.DataFrame([row_data])], ignore_index=True)

    # Save the combined DataFrame to a CSV file
    combined_df.to_csv('combined_output.csv', index=False)

    print("Data saved to 'combined_output.csv'")