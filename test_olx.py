import requests

SEARCH_QUERY = "nintendo 3ds"
MIN_PRICE = 250
MAX_PRICE = 600

# Full browser spoof headers to pass Cloudflare checks
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "ro-RO,ro;q=0.9,en-US;q=0.8,en;q=0.7",
    "Referer": "https://www.olx.ro/",
    "Origin": "https://www.olx.ro",
    "Sec-Ch-Ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin"
}

params = {
    "offset": 0,
    "limit": 30,
    "query": SEARCH_QUERY,
    "sort_by": "created_at:desc"
}

print(f"[*] Querying OLX Romania API for '{SEARCH_QUERY}'...")
session = requests.Session()
response = session.get("https://www.olx.ro/api/v1/offers/", headers=headers, params=params, timeout=15)

if response.status_code != 200:
    print(f"[!] OLX returned HTTP {response.status_code}")
    print(f"[!] Body snippet: {response.text[:200]}")
    exit(1)

offers = response.json().get("data", [])
print(f"[*] Successfully retrieved {len(offers)} raw listings from OLX.\n")

matches = 0
dropped = 0

for ad in offers:
    title = ad.get("title", "No Title")
    url = ad.get("url", "")
    
    price_val = None
    for p in ad.get("params", []):
        if p.get("key") == "price":
            price_val = p.get("value", {}).get("value")
            break

    if price_val is None:
        print(f"[-] DROPPED (No Price): {title}")
        dropped += 1
        continue

    # Strict price filter
    if price_val < MIN_PRICE or price_val > MAX_PRICE:
        print(f"[-] DROPPED ({price_val} RON out of range): {title}")
        dropped += 1
        continue

    city = ad.get("location", {}).get("city", {}).get("name", "România")
    print(f"\n[+] VALID MATCH: {title}")
    print(f"    Price:    {price_val} RON")
    print(f"    Location: {city}")
    print(f"    Link:     {url}\n")
    matches += 1

print("=" * 50)
print(f"TEST RESULT: {matches} valid matches kept | {dropped} dropped")
print("=" * 50)
