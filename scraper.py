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
            
            #print(full_url)
            
            card = link.parent
            for _ in range(6):
                if card is None:
                    continue
                if len(card.get_text()) > 200:
                    continue
                card = card.parent
                
            # get the info
            
            salary = ""
            if card:
                salary_text = card.get_text()
                match = re.search(r"NZD\s*[\d,]+(?:\s*[-–]\s*[\d,]+)?(?:\s*/\s*\w+)?", salary_text)
                if match:
                    # Also grab the "/Hour" or "/Year" suffix nearby
                    suffix_match = re.search(
                        r"(NZD\s*[\d,]+(?:\s*[-–]\s*[\d,]+)?)(\s*/\s*\w+)?",
                        salary_text
                    )
                    salary = suffix_match.group(0).strip() if suffix_match else match.group(0)
                    
            #print(salary)
            
            url_fields = href.split("/")
            
            company_name = url_fields[2]
            job_name = url_fields[-1]
            
            #print(company_name)
            #print(job_name)
            
            jobs.append({
                "job_name": job_name,
                "company": company_name,
                "url": full_url,
                "status": "unmarked"
            })
    return jobs


def scrape_seek():
    SEEK_URLS = [
        "https://www.seek.co.nz/internship-jobs/in-Christchurch-Canterbury?classification=6281",
        "https://www.seek.co.nz/summer-internship-in-jobs/in-Christchurch-Canterbury?classification=6281",
        "https://www.seek.co.nz/graduate-jobs/in-Christchurch-Canterbury?classification=6281",
        "https://www.seek.co.nz/jobs/in-Christchurch-Canterbury?keywords=software+intern&classification=6281",
    ]
 
    # Must be a CS/tech role
    CS_KEYWORDS = [
        "software", "developer", "engineer", "data", "computer science",
        "cs", "tech", "coding", "programming", "backend", "frontend",
        "full stack", "fullstack", "machine learning", "ml", "ai",
        "devops", "cloud", "cyber", "security",
    ]
 
    # Must also look like an entry-level/intern role
    INTERN_KEYWORDS = [
        "intern", "internship", "graduate", "grad", "entry level",
        "entry-level", "junior", "cadet", "trainee", "summer",
    ]
 
    def _is_cs_role(title: str) -> bool:
        t = title.lower()
        return any(kw in t for kw in CS_KEYWORDS)
 
    def _is_intern_role(title: str) -> bool:
        t = title.lower()
        return any(kw in t for kw in INTERN_KEYWORDS)
 
    def _title_to_slug(title: str, job_id: str) -> str:
        """Turn 'Software Engineer Summer Internship' into
        'software-engineer-summer-internship-92845177'."""
        slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
        return f"{slug}-{job_id}"
 
    def _company_slug(name: str) -> str:
        return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "unknown"
 
    def _scrape_url(url: str, page) -> list[dict]:
        print(f"  seek -> {url}")
        page.goto(url, wait_until="domcontentloaded", timeout=60_000)
        time.sleep(8)
        soup = BeautifulSoup(page.content(), "html.parser")
 
        results = []
        for card in soup.find_all("article", attrs={"data-testid": "job-card"}):
            title = card.get("aria-label", "").strip()
            if not title:
                continue
            if not _is_cs_role(title) or not _is_intern_role(title):
                continue
 
            job_id = card.get("data-job-id", "").strip()
            if not job_id:
                continue
 
            job_name = _title_to_slug(title, job_id)
            full_url = f"https://www.seek.co.nz/job/{job_id}"
 
            company_tag = card.find("a", attrs={"data-automation": "jobCompany"})
            company = _company_slug(parse_text(company_tag)) if company_tag else "unknown"
 
            results.append({
                "job_name": job_name,
                "company":  company,
                "url":      full_url,
                "status":   "unmarked",
            })
 
        return results
 
    all_jobs: list[dict] = []
    seen_ids: set[str] = set()
 
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(user_agent=(
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ))
 
        for url in SEEK_URLS:
            for job in _scrape_url(url, page):
                job_id = job["url"].split("/")[-1]
                if job_id not in seen_ids:
                    seen_ids.add(job_id)
                    all_jobs.append(job)
 
        browser.close()
 
    print(f"  seek -> {len(all_jobs)} unique CS intern listings found")
    return all_jobs



SCRAPER_FUNCS = [scrape_prosple, scrape_seek]

def get_scraper_funcs():
    return SCRAPER_FUNCS

if __name__ == "__main__":
    j = scrape_seek()
    for job in j:
        print(job)
        print('\n')
    #print(j)
    print(len(j))