import json
import requests

SEARCH_QUERY = "nintendo 3ds"
MIN_PRICE = 250
MAX_PRICE = 600

# Direct JSON endpoint for OLX Romania
API_URL = "https://www.olx.ro/api/v1/offers/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json"
}

params = {
    "offset": 0,
    "limit": 30,
    "query": SEARCH_QUERY,
    "sort_by": "created_at:desc"
}

print(f"[*] Querying OLX Romania API for '{SEARCH_QUERY}'...")
response = requests.get(API_URL, headers=HEADERS, params=params, timeout=15)

if response.status_code != 200:
    print(f"[!] OLX API returned error status: {response.status_code}")
    exit(1)

offers = response.json().get("data", [])
print(f"[*] Retrieved {len(offers)} raw listings from OLX.\n")

matches = 0
dropped = 0

for ad in offers:
    title = ad.get("title", "No Title")
    url = ad.get("url", "")
    
    # Extract the exact numeric price from OLX's internal parameter structure
    price_val = None
    for p in ad.get("params", []):
        if p.get("key") == "price":
            # OLX provides the raw numeric value directly
            price_val = p.get("value", {}).get("value")
            break

    # If item has no price or is exchange/free
    if price_val is None:
        print(f"[-] DROPPED (No Price): {title}")
        dropped += 1
        continue

    # STRICT CODE-LEVEL FILTER (Ignores whatever OLX does)
    if price_val < MIN_PRICE or price_val > MAX_PRICE:
        print(f"[-] DROPPED ({price_val} RON out of {MIN_PRICE}-{MAX_PRICE} range): {title}")
        dropped += 1
        continue

    # PASS: Matches your exact 250 - 600 RON bracket
    city = ad.get("location", {}).get("city", {}).get("name", "România")
    print(f"\n[+] VALID MATCH: {title}")
    print(f"    Price:    {price_val} RON")
    print(f"    Location: {city}")
    print(f"    Link:     {url}\n")
    matches += 1

print("=" * 50)
print(f"TEST SUMMARY: {matches} valid matches kept | {dropped} garbage listings dropped")
print("=" * 50)
