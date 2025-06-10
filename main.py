
import requests
import time
import hashlib

# Configuration utilisateur
TELEGRAM_BOT_TOKEN = "7968348098:AAEkwqQOGxpOXeTIzH8W4QSc5jAOSlRPrQA"
TELEGRAM_CHAT_ID = "5125163273"
LEBONCOIN_URL = "https://www.leboncoin.fr/recherche?category=17&shippable=1&phone_brand=apple&phone_model=iphone13pro,iphone14pro,iphone15&item_condition=7,5&transaction_status=search__no_value&owner_type=private&sort=time&order=desc"
CHECK_INTERVAL = 120  # En secondes (2 minutes)

# Pour stocker les annonces déjà envoyées
sent_ads = set()

def get_annonces():
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(LEBONCOIN_URL, headers=headers)
    if response.status_code == 200:
        if "/recherche?" in LEBONCOIN_URL:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, "html.parser")
            links = soup.find_all("a", href=True)
            results = []
            for link in links:
                href = link["href"]
                if href.startswith("/vi/") and href not in sent_ads:
                    full_url = "https://www.leboncoin.fr" + href
                    title = link.get_text(strip=True)
                    ad_hash = hashlib.md5(href.encode()).hexdigest()
                    results.append((ad_hash, title, full_url))
            return results
        else:
            print("L'URL n'est pas valide pour un scraping direct.")
            return []
    else:
        print("Erreur de requête :", response.status_code)
        return []

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    requests.post(url, data=payload)

print("🔍 Bot Leboncoin démarré...")

while True:
    try:
        annonces = get_annonces()
        for ad_hash, title, url in annonces:
            if ad_hash not in sent_ads:
                sent_ads.add(ad_hash)
                message = f"📱 <b>{title}</b>\n🔗 {url}"
                send_telegram_message(message)
        time.sleep(CHECK_INTERVAL)
    except Exception as e:
        print("Erreur pendant l'exécution :", e)
        time.sleep(60)
