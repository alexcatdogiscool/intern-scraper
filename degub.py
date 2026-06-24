"""
Run: python debug_company.py
Prints the full HTML of the first job card so we can find the company selector.
"""
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import time
 
URL = "https://www.seek.co.nz/internship-jobs?classification=6281"
 
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(user_agent=(
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ))
    page.goto(URL, wait_until="domcontentloaded", timeout=60_000)
    time.sleep(8)
    soup = BeautifulSoup(page.content(), "html.parser")
    browser.close()
 
card = soup.find("article", attrs={"data-testid": "job-card"})
if card:
    print(card.prettify())
else:
    print("no card found")