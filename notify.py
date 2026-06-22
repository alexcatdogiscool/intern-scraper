import os
from dotenv import load_dotenv

load_dotenv()

EMAIL_FROM = os.getenv("EMAIL")
APP_PASSWORD = os.getenv("APP_PASSWORD")


def email_jobs(new, unmarked):
    
    subject = f"{len(new)} new internships. {len(unmarked)} unmarked old internships"
    
    plain_lines = [f"{len(new)} New internships:"]
    for job in new:
        plain_lines += [
            f"Company: {job["company"]}",
            f"Job Name: {job["job_name"]}",
            f"Job URL: {job["url"]}",
            "================"
        ]
        
    plain_lines += ['\n' + "================"]
    plain_lines += ["Older Unmarked job listing"]
    for job in unmarked:
        plain_lines += [
            f"Company: {job["company"]}",
            f"Job Name: {job["job_name"]}",
            f"Job URL: {job["url"]}",
            "================"
        ]
        
    body_text = "\n".join(l for l in plain_lines if l)
    
    print(body_text)
    
    
        