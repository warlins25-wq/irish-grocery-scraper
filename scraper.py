import json
import time
from datetime import datetime
import requests

# Your ScraperAPI key
SCRAPERAPI_KEY = "f5202695409dccd4907fb09d688f9638"

CATEGORIES = ["milk", "bread", "butter", "eggs", "cheese"]

def fetch_tesco_products(term):
    catalog = []
    # Tesco Ireland internal grocery search API endpoint
    target_url = f"https://www.tesco.ie/groceries/en-IE/resources/search?query={term}"
    
    # Pass via ScraperAPI
    proxy_url = f"http://api.scraperapi.com?api_key={SCRAPERAPI_KEY}&url={target_url}"
    
    try:
        response = requests.get(proxy_url, timeout=30)
        if response.status_code == 200:
            data = response.json()
            # Extract products from Tesco API response payload
            items = data.get("uk", {}).get("ghs", {}).get("products", {}).get("results", [])
            
            for p in items[:10]:
                catalog.append({
                    "id": f"tesco_{p.get('id')}",
                    "name": p.get("title"),
                    "price": f"€{p.get('price')}",
                    "store": "Tesco Ireland",
                    "category": term,
                    "image_url": p.get("image"),
                    "last_updated": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
                })
            print(f"Tesco [{term}]: Found {len(catalog)} products")
        else:
            print(f"Tesco [{term}] returned status code: {response.status_code}")
    except Exception as e:
        print(f"Error fetching Tesco '{term}': {e}")
        
    return catalog

def main():
    database = []
    print("Starting Tesco-only extraction pipeline...")
    
    for term in CATEGORIES:
        print(f"Fetching Tesco category: {term}")
        items = fetch_tesco_products(term)
        database.extend(items)
        time.sleep(1)

    if not database:
        print("Tesco extraction returned zero items. Verify ScraperAPI key status.")
        database.append({
            "id": "status_check",
            "name": "System Status - Tesco Test Failed",
            "price": "€0.00",
            "store": "Tesco Ireland",
            "category": "Status",
            "last_updated": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        })

    print(f"Saving {len(database)} items into products.json...")
    with open("products.json", "w", encoding="utf-8") as f:
        json.dump(database, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
