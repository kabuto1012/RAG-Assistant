import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def scrape_page(target_url):
    url = "https://scrape.serper.dev"
    payload = json.dumps({"url": target_url})
    
    api_key = os.getenv("SERPER_API_KEY")
    if not api_key:
        print("[Scraper] Warning: SERPER_API_KEY not found. Web scraping functionality will not work.")
        return ""
    
    headers = {
        'X-API-KEY': api_key,
        'Content-Type': 'application/json'
    }

    response = requests.post(url, headers=headers, data=payload)

    if response.status_code != 200:
        print(f"[Scraper] Error: {response.status_code} {response.text}")
        return ""

    data = response.json()
    text_content = data.get("text", "")
    word_count = len(text_content.split())
    print(f"[Scraper] Scraped {word_count} words from {target_url}")
    return text_content

# if __name__ == "__main__":
#     url = "https://gamerant.com/red-dead-redemption-2-best-revolvers-locations/"
#     text = scrape_page(url)
#     print(text[:500]) # preview