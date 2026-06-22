import json
import re
import smtplib
import time
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
 
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright


def parse_text(el):
    return el.get_text(separator=" ", strip=True) if el else ""

def scrape_prosple():
    
    BASE_URL = "https://nz.prosple.com"
    
    url = ("https://nz.prosple.com/search-jobs"
        "?study_fields=506"
        "&work_mode=ON_SITE"
        "&search_radius=50"
        "&location=Christchurch%2C+CA%2C+New+Zealand"
    )
    
    jobs = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
                
            )
        )
        
        # load the page
        print("loading da page")
        
        page.goto(url, wait_until="domcontentloaded", timeout=60_000)
        
        try:
            page.wait_for_selector(
                'a[href*="/jobs-internships/"]',
                timeout=20_000
            )
        except Exception:
            print(f"no job links are here...")
        
        time.sleep(5)
        
        html = page.content()
        browser.close()
        
        ## we now have the page html we need
        
        soup = BeautifulSoup(html, "html.parser")
        
        job_links = soup.find_all(
            "a",
            href=re.compile(r"^/graduate-employers/.+/jobs-internships/.+")
        )
        
        jobs = []
        seen_hrefs = set()
        
        for link in job_links:
            href = link.get("href", "")
            if not href or href in seen_hrefs:
                continue
            seen_hrefs.add(href)
            
            title = parse_text(link)
            if not title:
                continue
            
            full_url = BASE_URL + href
            
            job_id = href.rstrip("/").split("/")[-1]
            
            print(full_url)
        




SCRAPER_FUNCS = [scrape_prosple]

if __name__ == "__main__":
    scrape_prosple()