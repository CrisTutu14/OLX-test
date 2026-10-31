import os
from curl_cffi import requests

SEARCH_QUERY = "nintendo 3ds"
MIN_PRICE = 250
MAX_PRICE = 600

TARGET_HARDWARE = ["3ds", "2ds"]
CLONE_HANDHELDS = ["trimui", "anbernic", "r36s", "miyoo", "powkiddy", "data frog"]

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
SEEN_FILE = "seen_ids.txt"

def send_telegram_alert(title, price, city, url):
    if not BOT_TOKEN or not CHAT_ID:
        print("[!] Telegram credentials missing. Skipping notification.")
        return
    text = (
        f"🚨 <b>New Nintendo 3DS Listing!</b>\n\n"
        f"🕹 <b>Title:</b> {title}\n"
        f"💰 <b>Price:</b> {price} RON\n"
        f"📍 <b>Location:</b> {city}\n\n"
        f"🔗 <a href='{url}'>Open OLX Listing</a>"
    )
    tg_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    try:
        requests.post(tg_url, json=payload, timeout=10)
    except Exception as e:
        print(f"[!] Failed to send Telegram alert: {e}")

# Load previously alerted IDs
seen_ids = set()
if os.path.exists(SEEN_FILE):
    with open(SEEN_FILE, "r") as f:
        seen_ids = {line.strip() for line in f if line.strip()}

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

response = requests.get(url, params=params, headers=headers, impersonate="chrome120", timeout=15)
if response.status_code != 200:
    print(f"[!] OLX returned HTTP {response.status_code}")
    exit(1)

offers = response.json().get("data", [])
new_matches = 0

for ad in offers:
    ad_id = str(ad.get("id"))
    title = ad.get("title", "No Title")
    ad_url = ad.get("url", "")
    title_lower = title.lower()

    # Skip if we already sent this listing
    if ad_id in seen_ids:
        continue

    # 1. Price check
    price_val = None
    for p in ad.get("params", []):
        if p.get("key") == "price":
            price_val = p.get("value", {}).get("value")
            break

    if price_val is None or price_val < MIN_PRICE or price_val > MAX_PRICE:
        continue

    # 2. Hardware check
    if not any(target in title_lower for target in TARGET_HARDWARE):
        continue

    # 3. Clone check
    if any(clone in title_lower for clone in CLONE_HANDHELDS):
        continue

    # Pass condition
    city = ad.get("location", {}).get("city", {}).get("name", "România")
    print(f"[+] NEW MATCH FOUND: {title} ({price_val} RON)")
    send_telegram_alert(title, price_val, city, ad_url)
    
    seen_ids.add(ad_id)
    new_matches += 1

# Save state back to file
with open(SEEN_FILE, "w") as f:
    for item_id in seen_ids:
        f.write(f"{item_id}\n")

print(f"[*] Complete. {new_matches} new alert(s) sent.")
