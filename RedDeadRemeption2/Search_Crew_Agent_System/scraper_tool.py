import requests
import json

def scrape_page(target_url):
    url = "https://scrape.serper.dev"
    payload = json.dumps({"url": target_url})
    headers = {
        'X-API-KEY': 'YOUR_API_KEY_HERE',
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