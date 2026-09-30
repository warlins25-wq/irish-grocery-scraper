import json
import time
from datetime import datetime
import requests
from bs4 import BeautifulSoup

# Paste your free key from scraperapi.com here
SCRAPERAPI_KEY = "f5202695409dccd4907fb09d688f9638"

CATEGORIES = [
    "milk", "bread", "butter", "eggs", "cheese",
    "chicken", "apples", "bananas", "coffee", "tea"
]

def fetch_dunnes_with_proxy(term):
    catalog = []
    # Target Dunnes public web search page
    target_url = f"https://www.dunnesstoresgrocery.com/sm/delivery/rs-ie/results?q={term}"
    
    # render=true forces ScraperAPI to execute JavaScript and pass Cloudflare challenges
    proxy_url = f"http://api.scraperapi.com?api_key={SCRAPERAPI_KEY}&url={target_url}&render=true"
    
    try:
        res = requests.get(proxy_url, timeout=60)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")
            # Parse product tiles from rendered HTML
            product_cards = soup.find_all("article") or soup.find_all("div", class_=lambda c: c and "ProductCard" in c)
            
            for idx, card in enumerate(product_cards[:10]):
                name_el = card.find("h3") or card.find("a")
                price_el = card.find("span", text=lambda t: t and "€" in t) or card.find("span", class_=lambda c: c and "price" in str(c).lower())
                
                if name_el:
                    item_name = name_el.text.strip()
                    item_price = price_el.text.strip() if price_el else "€0.00"
                    
                    catalog.append({
                        "id": f"dunnes_{term}_{idx}",
                        "name": item_name,
                        "price": item_price,
                        "store": "Dunnes Stores",
                        "category": term,
                        "last_updated": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
                    })
            print(f"Dunnes [{term}]: Found {len(catalog)} products")
    except Exception as e:
        print(f"Error fetching Dunnes {term}: {e}")
        
    return catalog

def main():
    database = []
    print("Starting ScraperAPI job...")
    
    for term in CATEGORIES[:5]:  # Limit initial query batch to test key & save API credits
        print(f"Fetching category: {term}")
        items = fetch_dunnes_with_proxy(term)
        database.extend(items)
        time.sleep(2)

    if not database:
        print("ScraperAPI verification failed.")
        database.append({
            "id": "status_check",
            "name": "System Status - Verify ScraperAPI Key or Target Site Structure",
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
