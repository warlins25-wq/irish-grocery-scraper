import json
import time
from datetime import datetime
import requests

# Your ScraperAPI Key
SCRAPERAPI_KEY = "f5202695409dccd4907fb09d688f9638"

CATEGORIES = [
    "milk", "bread", "butter", "eggs", "cheese",
    "chicken", "apples", "bananas", "coffee", "tea"
]

def fetch_dunnes_products(term):
    catalog = []
    # Direct internal API endpoint used by Dunnes web frontend
    target_api = f"https://www.dunnesstoresgrocery.com/api/v1/products/search?q={term}"
    
    # Query ScraperAPI using standard API proxy mode
    proxy_url = f"http://api.scraperapi.com?api_key={SCRAPERAPI_KEY}&url={target_api}"
    
    try:
        response = requests.get(proxy_url, timeout=30)
        if response.status_code == 200:
            data = response.json()
            # Extract product array from API payload
            items = data.get("products", []) or data.get("data", {}).get("products", [])
            
            for p in items[:10]:
                catalog.append({
                    "id": f"dunnes_{p.get('id') or p.get('sku')}",
                    "name": p.get("name") or p.get("title"),
                    "price": f"€{p.get('price')}" if "€" not in str(p.get("price")) else str(p.get("price")),
                    "store": "Dunnes Stores",
                    "category": term,
                    "image_url": p.get("image") or p.get("imageUrl"),
                    "last_updated": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
                })
            print(f"Successfully scraped Dunnes [{term}]: {len(catalog)} items")
    except Exception as e:
        print(f"Error fetching Dunnes category '{term}': {e}")
        
    return catalog

def main():
    database = []
    print("Starting direct API proxy ingestion...")
    
    for term in CATEGORIES:
        print(f"Processing category: {term}")
        items = fetch_dunnes_products(term)
        database.extend(items)
        time.sleep(1)

    if not database:
        print("ScraperAPI request returned zero results.")
        database.append({
            "id": "status_check",
            "name": "System Status - Unable to query store API",
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
