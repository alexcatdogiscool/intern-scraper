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

def scrape_linkedin():
    import requests
    import random
 
    QUERY = {
        "keyword":           "Software Engineer Intern",
        "location":          "New Zealand",
        "job_type":          "internship",
        "experience_level":  "internship",
        "date_since_posted": "past month",
        "sort_by":           "recent",
        "limit":             10,   # always keep this an int, never a string
    }
 
    DATE_MAP       = {"past month": "r2592000", "past week": "r604800", "24hr": "r86400"}
    EXPERIENCE_MAP = {"internship": "1", "entry level": "2", "associate": "3",
                      "senior": "4", "director": "5", "executive": "6"}
    JOB_TYPE_MAP   = {"full time": "F", "full-time": "F", "part time": "P",
                      "part-time": "P", "contract": "C", "temporary": "T",
                      "volunteer": "V", "internship": "I"}
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/119.0.0.0 Safari/537.36",
    ]
 
    # Guarantee limit is an int so comparisons never throw TypeError
    limit = int(QUERY["limit"])
 
    def _build_url(start):
        base = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?"
        params = {}
        if QUERY.get("keyword"):
            params["keywords"] = QUERY["keyword"].strip().replace(" ", "+")
        if QUERY.get("location"):
            params["location"] = QUERY["location"].strip().replace(" ", "+")
        if DATE_MAP.get(QUERY.get("date_since_posted", "").lower()):
            params["f_TPR"] = DATE_MAP[QUERY["date_since_posted"].lower()]
        if EXPERIENCE_MAP.get(QUERY.get("experience_level", "").lower()):
            params["f_E"] = EXPERIENCE_MAP[QUERY["experience_level"].lower()]
        if JOB_TYPE_MAP.get(QUERY.get("job_type", "").lower()):
            params["f_JT"] = JOB_TYPE_MAP[QUERY["job_type"].lower()]
        params["start"] = start
        if QUERY.get("sort_by") == "recent":
            params["sortBy"] = "DD"
        return base + "&".join(f"{k}={v}" for k, v in params.items())
 
    def _fetch_batch(start):
        headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.linkedin.com/jobs",
            "X-Requested-With": "XMLHttpRequest",
        }
        resp = requests.get(_build_url(start), headers=headers, timeout=10)
        if resp.status_code == 429:
            raise Exception("rate limited — wait a few minutes before retrying")
        if resp.status_code != 200:
            raise Exception(f"HTTP {resp.status_code}")
 
        soup = BeautifulSoup(resp.text, "html.parser")
        jobs = []
        for li in soup.find_all("li"):
            position    = parse_text(li.find(class_="base-search-card__title"))
            company     = parse_text(li.find(class_="base-search-card__subtitle"))
            if not position or not company:
                continue
            url_tag     = li.find("a", class_="base-card__full-link")
            job_url     = url_tag["href"] if url_tag else ""
            job_name    = re.sub(r"[^a-z0-9]+", "-", f"{position}-{company}".lower()).strip("-")
            company_slug = re.sub(r"[^a-z0-9]+", "-", company.lower()).strip("-")
            jobs.append({"job_name": job_name, "company": company_slug,
                         "url": job_url, "status": "unmarked"})
        return jobs
 
    all_jobs: list[dict] = []
    seen_names: set[str] = set()
    start = 0
    BATCH_SIZE = 25
 
    print(f"  linkedin -> fetching '{QUERY['keyword']}' in '{QUERY['location']}' (limit={limit})")
 
    while True:
        try:
            batch = _fetch_batch(start)
        except Exception as e:
            print(f"  linkedin -> fetch error at start={start}: {e}")
            break  # return whatever we collected so far
 
        if not batch:
            print(f"  linkedin -> empty page at start={start}, stopping")
            break
 
        for job in batch:
            if job["job_name"] not in seen_names:
                seen_names.add(job["job_name"])
                all_jobs.append(job)
 
        print(f"  linkedin -> collected {len(all_jobs)} so far")
 
        if limit and len(all_jobs) >= limit:
            all_jobs = all_jobs[:limit]
            break
 
        start += BATCH_SIZE
        time.sleep(2 + random.random())
 
    print(f"  linkedin -> {len(all_jobs)} listings found")
    return all_jobs

SCRAPER_FUNCS = [scrape_prosple, scrape_seek, scrape_linkedin]

def get_scraper_funcs():
    return SCRAPER_FUNCS

if __name__ == "__main__":
    j = scrape_linkedin()
    for job in j:
        print(job)
        print('\n')
    #print(j)
    print(len(j))