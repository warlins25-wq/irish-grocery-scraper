import json
import time
from datetime import datetime
import requests

# 1. Paste your free key from scraperapi.com here
SCRAPERAPI_KEY = "f5202695409dccd4907fb09d688f9638"

CATEGORIES = [
    "milk", "bread", "butter", "eggs", "cheese",
    "chicken", "apples", "bananas", "coffee", "tea"
]

def fetch_dunnes_with_proxy(term):
    catalog = []
    # Target URL on Dunnes Stores
    target_url = f"https://www.dunnesstoresgrocery.com/api/v1/products/search?q={term}"
    
    # Route through ScraperAPI to bypass anti-bot & IP bans
    proxy_url = f"http://api.scraperapi.com?api_key={SCRAPERAPI_KEY}&url={target_url}"
    
    try:
        res = requests.get(proxy_url, timeout=30)
        if res.status_code == 200:
            data = res.json()
            products = data.get("products", [])
            for p in products[:10]:
                catalog.append({
                    "id": f"dunnes_{p.get('sku') or p.get('id')}",
                    "name": p.get("name"),
                    "price": f"€{p.get('price')}" if "€" not in str(p.get("price")) else str(p.get("price")),
                    "store": "Dunnes Stores",
                    "category": term,
                    "image_url": p.get("image"),
                    "last_updated": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
                })
            print(f"Dunnes [{term}]: Successfully extracted {len(products)} items")
    except Exception as e:
        print(f"Error on Dunnes {term}: {e}")
        
    return catalog

def main():
    database = []
    print("Starting proxy-assisted scraping job...")
    
    for term in CATEGORIES:
        print(f"Fetching category: {term}")
        items = fetch_dunnes_with_proxy(term)
        database.extend(items)
        time.sleep(1)

    if not database:
        print("Fallback triggered. Verify your ScraperAPI key.")
        database.append({
            "id": "status_check",
            "name": "System Status - Check ScraperAPI Key",
            "price": "€0.00",
            "store": "System",
            "category": "Status",
            "last_updated": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        })

    print(f"Saving {len(database)} items into products.json...")
    with open("products.json", "w", encoding="utf-8") as f:
        json.dump(database, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
