import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def search_top_results(query, top_n=1, exclude_domains=["reddit.com", "quora.com", "youtube.com"]):
    url = "https://google.serper.dev/search"
    payload = json.dumps({"q": query})
    
    api_key = os.getenv("SERPER_API_KEY")
    if not api_key:
        print("[Search] Warning: SERPER_API_KEY not found. Web search functionality will not work.")
        return []
    
    headers = {
        'X-API-KEY': api_key,
        'Content-Type': 'application/json'
    }

    response = requests.post(url, headers=headers, data=payload)

    if response.status_code != 200:
        print(f"[Search] Error: {response.status_code} {response.text}")
        return []

    data = response.json()
    organic_results = data.get("organic", [])

    filtered_results = []
    for res in organic_results:
        if exclude_domains and any(domain in res['link'] for domain in exclude_domains):
            continue
        filtered_results.append(res['link'])
        if len(filtered_results) == top_n:
            break

    return filtered_results

# if __name__ == "__main__":
#     urls = search_top_results("best revolver in Red Dead Redemption 2")
#     print("Top URLs:", urls)
