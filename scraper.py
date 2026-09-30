import json
import time
from datetime import datetime
import requests

# Mimic a full modern desktop browser to avoid silent blocking
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-IE,en-GB;q=0.9,en;q=0.8",
    "Referer": "https://www.dunnesstoresgrocery.com/",
}

CATEGORIES = [
    "milk", "bread", "butter", "eggs", "cheese", 
    "chicken", "apples", "bananas", "coffee", "tea",
    "pasta", "rice", "cereal", "yogurt", "water"
]

def fetch_dunnes_items():
    catalog = []
    print("--- Scraping Dunnes Stores ---")
    for cat in CATEGORIES:
        url = f"https://www.dunnesstoresgrocery.com/api/v1/products/search?q={cat}"
        try:
            res = requests.get(url, headers=HEADERS, timeout=10)
            if res.status_code == 200:
                data = res.json()
                products = data.get("products", [])
                for p in products[:15]:  # Get top items per search
                    catalog.append({
                        "id": f"dunnes_{p.get('sku') or p.get('id')}",
                        "name": p.get("name"),
                        "price": f"€{p.get('price')}" if "€" not in str(p.get("price")) else str(p.get("price")),
                        "store": "Dunnes Stores",
                        "category": cat,
                        "image_url": p.get("image"),
                        "last_updated": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
                    })
                print(f"Dunnes [{cat}]: Found {len(products)} products")
            time.sleep(1)
        except Exception as e:
            print(f"Error fetching Dunnes category {cat}: {e}")
    return catalog

def main():
    database = []
    
    # Run extraction
    dunnes_data = fetch_dunnes_items()
    database.extend(dunnes_data)
    
    # If API blocked or empty, fallback with a dummy verification item so the file is never 0 bytes
    if not database:
        print("Warning: Live extractions returned empty. Adding fallback status item.")
        database.append({
            "id": "status_check",
            "name": "System Status - Online",
            "price": "€0.00",
            "store": "System",
            "category": "Status",
            "last_updated": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        })

    print(f"Saving {len(database)} total items into products.json...")
    with open("products.json", "w", encoding="utf-8") as f:
        json.dump(database, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
