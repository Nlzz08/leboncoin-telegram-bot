import asyncio
from playwright.async_api import async_playwright
import os
import requests
import hashlib
from bs4 import BeautifulSoup

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("CHAT_ID")
LBC_URL = os.getenv("LBC_URL")

sent_ads = set()

async def scrape():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(LBC_URL)
        content = await page.content()
        await browser.close()
        return content

def parse_ads(html):
    soup = BeautifulSoup(html, "html.parser")
    ads = []
    for link in soup.find_all("a", href=True):
        href = link['href']
        if href.startswith("/vi/"):
            ad_hash = hashlib.md5(href.encode()).hexdigest()
            title = link.get_text(strip=True)
            url = "https://www.leboncoin.fr" + href
            ads.append((ad_hash, title, url))
    return ads

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    requests.post(url, data=payload)

async def main():
    global sent_ads
    print("Bot démarré...")
    while True:
        html = await scrape()
        ads = parse_ads(html)
        new = False
        for ad_hash, title, url in ads:
            if ad_hash not in sent_ads:
                sent_ads.add(ad_hash)
                message = f"📱 <b>{title}</b>\n🔗 {url}"
                send_telegram_message(message)
                print("Annonce envoyée:", title)
                new = True
        if not new:
            print("Pas de nouvelle annonce.")
        await asyncio.sleep(120)

if __name__ == "__main__":
    asyncio.run(main())
