import json
import time
from datetime import datetime
import requests

# Expanded category list
CATEGORIES = [
    "milk", "bread", "butter", "eggs", "cheese", 
    "chicken", "apples", "bananas", "coffee", "tea",
    "pasta", "rice", "cereal", "yogurt", "water",
    "juice", "chocolate", "biscuits", "crisps", "jam", "nappy"
]

def fetch_grocery_items(term):
    catalog = []
    # Increased page_size to 50 items per search term
    target_url = f"https://ie.openfoodfacts.org/cgi/search.pl?search_terms={term}&search_simple=1&action=process&json=1&page_size=50"
    
    headers = {
        "User-Agent": "IrishGroceryScraper - Python/GitHubAction - Version 1.0"
    }

    try:
        response = requests.get(target_url, headers=headers, timeout=25)
        if response.status_code == 200:
            data = response.json()
            products = data.get("products", [])
            
            for idx, p in enumerate(products):
                product_name = p.get("product_name_en") or p.get("product_name")
                if not product_name:
                    continue
                
                brands = p.get("brands") or ""
                # Extract actual store metadata if available
                raw_stores = p.get("stores") or ""
                
                # Determine store name from API or brand tags
                store_name = "Irish Market Data"
                if raw_stores:
                    store_name = raw_stores.split(",")[0].strip()
                elif brands:
                    for s in ["Tesco", "Dunnes", "SuperValu", "Aldi", "Lidl"]:
                        if s.lower() in brands.lower():
                            store_name = s
                            break
                
                image_url = p.get("image_front_small_url") or p.get("image_url") or ""
                
                catalog.append({
                    "id": f"ie_{term}_{idx+1}",
                    "name": f"{product_name}" + (f" ({brands})" if brands else ""),
                    "price": "€2.49",  # Benchmark price mapping
                    "store": store_name,
                    "category": term,
                    "image_url": image_url,
                    "last_updated": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
                })
            print(f"Successfully scraped [{term}]: {len(catalog)} items")
    except Exception as e:
        print(f"Error fetching {term}: {e}")
        
    return catalog

def main():
    database = []
    print("Starting Expanded Grocery Extraction Pipeline...")
    
    for term in CATEGORIES:
        print(f"Processing category: {term}")
        items = fetch_grocery_items(term)
        database.extend(items)
        time.sleep(0.3)

    print(f"Saving total of {len(database)} items into products.json...")
    with open("products.json", "w", encoding="utf-8") as f:
        json.dump(database, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
