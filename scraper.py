import json
import time
from datetime import datetime
import requests

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/118.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-IE,en-GB;q=0.9,en;q=0.8",
}

# Main departments to crawl full stock
TESCO_DEPARTMENTS = [
    "fresh-food",
    "bakery",
    "frozen-food",
    "treats-and-snacks",
    "food-cupboard",
    "drinks",
    "health-and-beauty",
    "household",
    "baby"
]

DUNNES_CATEGORIES = [
    "fresh-food",
    "food-cupboard",
    "frozen",
    "drinks",
    "bakery",
    "toiletries",
    "household",
    "baby"
]

def crawl_tesco():
    catalog = []
    print("--- Crawling Tesco Ireland ---")
    for dept in TESCO_DEPARTMENTS:
        page = 1
        max_pages = 10  # Pages per department to capture full stock
        while page <= max_pages:
            url = f"https://www.tesco.ie/groceries/en-IE/shop/{dept}/all?page={page}&count=48"
            try:
                res = requests.get(url, headers=HEADERS, timeout=12)
                if res.status_code != 200:
                    break
                
                data = res.json() if "application/json" in res.headers.get("Content-Type", "") else None
                if not data or not data.get("items"):
                    break
                    
                items = data.get("items", [])
                for item in items:
                    catalog.append({
                        "id": f"tesco_{item.get('id')}",
                        "name": item.get("title"),
                        "price": f"€{item.get('price')}",
                        "unit_price": item.get("unitPrice"),
                        "category": dept,
                        "store": "Tesco Ireland",
                        "image_url": item.get("image"),
                        "last_updated": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
                    })
                
                print(f"Tesco [{dept}] - Page {page}: Found {len(items)} items")
                page += 1
                time.sleep(1.5)
            except Exception as e:
                print(f"Error on Tesco {dept} p.{page}: {e}")
                break
    return catalog

def crawl_dunnes():
    catalog = []
    print("--- Crawling Dunnes Stores ---")
    for cat in DUNNES_CATEGORIES:
        page = 1
        while page <= 15:
            url = f"https://www.dunnesstoresgrocery.com/api/v1/categories/{cat}/products?page={page}&pageSize=60"
            try:
                res = requests.get(url, headers=HEADERS, timeout=12)
                if res.status_code != 200:
                    break
                    
                data = res.json()
                products = data.get("products", [])
                if not products:
                    break
                    
                for p in products:
                    catalog.append({
                        "id": f"dunnes_{p.get('sku') or p.get('id')}",
                        "name": p.get("name"),
                        "price": str(p.get("price")) if "€" in str(p.get("price")) else f"€{p.get('price')}",
                        "category": cat,
                        "store": "Dunnes Stores",
                        "image_url": p.get("image"),
                        "last_updated": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
                    })
                    
                print(f"Dunnes [{cat}] - Page {page}: Found {len(products)} items")
                page += 1
                time.sleep(1.5)
            except Exception as e:
                print(f"Error on Dunnes {cat} p.{page}: {e}")
                break
    return catalog

def main():
    single_file_database = []
    
    # 1. Pull Tesco
    tesco_items = crawl_tesco()
    single_file_database.extend(tesco_items)
    
    # 2. Pull Dunnes
    dunnes_items = crawl_dunnes()
    single_file_database.extend(dunnes_items)
    
    # 3. Save EVERYTHING into 1 single file: products.json
    print(f"Saving total dataset ({len(single_file_database)} items) into products.json...")
    with open("products.json", "w", encoding="utf-8") as f:
        json.dump(single_file_database, f, indent=2, ensure_ascii=False)
        
    print("Done! Single file updated successfully.")

if __name__ == "__main__":
    main()
