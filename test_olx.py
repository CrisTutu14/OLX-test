from curl_cffi import requests

SEARCH_QUERY = "nintendo 3ds"
MIN_PRICE = 250
MAX_PRICE = 600

# Must have one of these in the title
TARGET_HARDWARE = ["3ds", "2ds"]

# Obvious non-Nintendo retro clones that stuff 3DS in their title/tags
CLONE_HANDHELDS = ["trimui", "anbernic", "r36s", "miyoo", "powkiddy", "data frog"]

url = "https://www.olx.ro/api/v1/offers/"
params = {
    "offset": 0,
    "limit": 30,
    "query": SEARCH_QUERY,
    "sort_by": "created_at:desc"
}

headers = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "ro-RO,ro;q=0.9,en-US;q=0.8,en;q=0.7",
    "Referer": "https://www.olx.ro/",
    "Origin": "https://www.olx.ro"
}

print(f"[*] Querying OLX Romania API with Chrome TLS fingerprint...")

response = requests.get(
    url,
    params=params,
    headers=headers,
    impersonate="chrome120",
    timeout=15
)

if response.status_code != 200:
    print(f"[!] OLX returned HTTP {response.status_code}")
    exit(1)

offers = response.json().get("data", [])
print(f"[*] Successfully retrieved {len(offers)} raw listings from OLX.\n")

matches = 0
dropped = 0

for ad in offers:
    title = ad.get("title", "No Title")
    ad_url = ad.get("url", "")
    title_lower = title.lower()
    
    # 1. Price check
    price_val = None
    for p in ad.get("params", []):
        if p.get("key") == "price":
            price_val = p.get("value", {}).get("value")
            break

    if price_val is None:
        print(f"[-] DROPPED (No Price): {title}")
        dropped += 1
        continue

    if price_val < MIN_PRICE or price_val > MAX_PRICE:
        print(f"[-] DROPPED ({price_val} RON out of range): {title}")
        dropped += 1
        continue

    # 2. Hardware check: must contain '3ds' or '2ds'
    if not any(target in title_lower for target in TARGET_HARDWARE):
        print(f"[-] DROPPED (Not a 3DS/2DS console/bundle): {title}")
        dropped += 1
        continue

    # 3. Clone check: reject emulation consoles
    if any(clone in title_lower for clone in CLONE_HANDHELDS):
        print(f"[-] DROPPED (Emulation handheld): {title}")
        dropped += 1
        continue

    # Listing passes all checks
    city = ad.get("location", {}).get("city", {}).get("name", "România")
    print(f"\n[+] VALID MATCH: {title}")
    print(f"    Price:    {price_val} RON")
    print(f"    Location: {city}")
    print(f"    Link:     {ad_url}\n")
    matches += 1

print("=" * 50)
print(f"TEST RESULT: {matches} valid matches kept | {dropped} dropped")
print("=" * 50)
