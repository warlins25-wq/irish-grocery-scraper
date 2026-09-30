import json
import time
from datetime import datetime
import requests

# Categories to fetch from Open Food Facts (Ireland market)
CATEGORIES = ["milk", "bread", "butter", "eggs", "cheese", "coffee", "tea"]

def fetch_grocery_items(term):
    catalog = []
    # Open Food Facts API targeting products in Ireland
    target_url = f"https://ie.openfoodfacts.org/cgi/search.pl?search_terms={term}&search_simple=1&action=process&json=1&page_size=5"
    
    headers = {
        "User-Agent": "IrishGroceryScraper - Python/GitHubAction - Version 1.0"
    }

    try:
        response = requests.get(target_url, headers=headers, timeout=20)
        if response.status_code == 200:
            data = response.json()
            products = data.get("products", [])
            
            for idx, p in enumerate(products):
                product_name = p.get("product_name_en") or p.get("product_name") or f"{term.capitalize()} Item {idx+1}"
                brands = p.get("brands") or "Generic Store Brand"
                image_url = p.get("image_front_small_url") or p.get("image_url") or ""
                
                catalog.append({
                    "id": f"ie_{term}_{idx+1}",
                    "name": f"{product_name} ({brands})",
                    "price": "€1.99",  # Standard baseline price for sample catalog mapping
                    "store": "Irish Market Data",
                    "category": term,
                    "image_url": image_url,
                    "last_updated": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
                })
            print(f"Successfully scraped [{term}]: {len(catalog)} items")
        else:
            print(f"Request failed for {term}: Status {response.status_code}")
    except Exception as e:
        print(f"Error fetching {term}: {e}")
        
    return catalog

def main():
    database = []
    print("Starting Grocery Extraction Pipeline...")
    
    for term in CATEGORIES:
        print(f"Processing category: {term}")
        items = fetch_grocery_items(term)
        database.extend(items)
        time.sleep(0.5)

    if not database:
        print("Scraper returned zero items.")
        database.append({
            "id": "status_check",
            "name": "System Status - No products returned",
            "price": "€0.00",
            "store": "System",
            "category": "Status",
            "last_updated": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        })

    print(f"Saving {len(database)} items to products.json...")
    with open("products.json", "w", encoding="utf-8") as f:
        json.dump(database, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
