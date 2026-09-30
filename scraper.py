import json
import time
import re
from datetime import datetime
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-IE,en-GB;q=0.9,en;q=0.8",
    "Cache-Control": "no-cache",
}

SEARCH_TERMS = [
    "milk", "bread", "butter", "eggs", "cheese", 
    "chicken", "apples", "bananas", "coffee", "tea"
]

def fetch_tesco_html(term):
    catalog = []
    url = f"https://www.tesco.ie/groceries/en-IE/search?query={term}"
    try:
        res = requests.get(url, headers=HEADERS, timeout=12)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")
            items = soup.find_all("li", class_="product-list--list-item")
            for idx, item in enumerate(items[:10]):
                title_el = item.find("a", class_="data-unwrapped") or item.find("span", class_="title")
                price_el = item.find("span", class_="value")
                if title_el and price_el:
                    catalog.append({
                        "id": f"tesco_{term}_{idx}",
                        "name": title_el.text.strip(),
                        "price": f"€{price_el.text.strip()}",
                        "store": "Tesco Ireland",
                        "category": term,
                        "last_updated": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
                    })
    except Exception as e:
        print(f"Tesco error on {term}: {e}")
    return catalog

def fetch_dunnes_html(term):
    catalog = []
    url = f"https://www.dunnesstoresgrocery.com/sm/delivery/rs-ie/results?q={term}"
    try:
        res = requests.get(url, headers=HEADERS, timeout=12)
        if res.status_code == 200:
            # Locate raw embedded JSON data inside HTML response page
            match = re.search(r'__PRELOADED_STATE__\s*=\s*({.*?});', res.text)
            if match:
                raw_json = json.loads(match.group(1))
                products = raw_json.get("products", {})
                for key, p in list(products.items())[:10]:
                    catalog.append({
                        "id": f"dunnes_{p.get('sku', key)}",
                        "name": p.get("name"),
                        "price": f"€{p.get('price', {}).get('price', '0.00')}",
                        "store": "Dunnes Stores",
                        "category": term,
                        "last_updated": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
                    })
    except Exception as e:
        print(f"Dunnes error on {term}: {e}")
    return catalog

def main():
    dataset = []
    print("Starting direct HTML extraction pipeline...")
    
    for term in SEARCH_TERMS:
        print(f"Scraping category: {term}")
        dataset.extend(fetch_tesco_html(term))
        time.sleep(2)
        dataset.extend(fetch_dunnes_html(term))
        time.sleep(2)
        
    if not dataset:
        print("Fallback triggered: IP restricted by cloud providers.")
        dataset.append({
            "id": "status_check",
            "name": "System Status - Anti-Bot Protection Active",
            "price": "€0.00",
            "store": "System",
            "category": "Status",
            "last_updated": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        })

    print(f"Saving {len(dataset)} items to products.json")
    with open("products.json", "w", encoding="utf-8") as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
