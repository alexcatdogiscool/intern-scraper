import json
from pathlib import Path



SEEN_IDS_FILE = Path(__file__).parent / "seen_jobs.json"
ALL_JOBS_FILE = Path(__file__).parent / "all_jobs.json"


def load_seen_ids():
    if SEEN_IDS_FILE.exists():
        with open(SEEN_IDS_FILE) as f:
            return set(json.load(f))
    return set()

def save_seen_ids(seen: set):
    with open(SEEN_IDS_FILE, "w") as f:
        json.dump(sorted(seen), f, indent=2)
        
def load_all_jobs() -> list:
    if ALL_JOBS_FILE.exists():
        with open(ALL_JOBS_FILE) as f:
            return json.load(f)
    return []

def save_all_jobs(jobs: list):
    with open(ALL_JOBS_FILE, "w") as f:
        json.dump(jobs, f, indent=2)
        
def load_unmarked_jobs() -> list:
    """Return jobs that haven't been marked/actioned yet."""
    return [j for j in load_all_jobs() if j.get("status") == "unmarked"]
        
def update_status(job_name, comapny, new_status):
    jobs = load_all_jobs()
    for job in jobs:
        if job["job_name"] == job_name and job["company"] == comapny:
            job["status"] = new_status
            break
    
    with open(ALL_JOBS_FILE, 'w') as f:
        json.dump(jobs, f, indent=2)
        

def get_unique_jobs(jobs: list) -> list:
    
    seen_ids = load_seen_ids()
    
    new_jobs = [j for j in jobs if j["job_name"] not in seen_ids]
    
    if not new_jobs:
        print("no new job listings")
        return []
    
    print("new jobs have come up!!")
    
    all_jobs = load_all_jobs()
    all_jobs.extend(new_jobs)
    save_all_jobs(all_jobs)
    
    for j in new_jobs:
        seen_ids.add(j["job_name"])
    save_seen_ids(seen_ids)
    
    return new_jobs
    
    
        