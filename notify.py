import os
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import yagmail

load_dotenv()

EMAIL_FROM = os.getenv("EMAIL")
EMAIL_TO = os.getenv("EMAIL")

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
    plain_lines += ["Older Unmarked job listing:" + '\n']
    for job in unmarked:
        plain_lines += [
            f"Company: {job["company"]}",
            f"Job Name: {job["job_name"]}",
            f"Job URL: {job["url"]}",
            "================"
        ]
        
    body_text = "\n".join(l for l in plain_lines if l)
    
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["FROM"] = EMAIL_FROM
    msg["TO"] = EMAIL_FROM
    msg.attach(MIMEText(body_text, "plain"))
    
    try:
        yag = yagmail.SMTP(EMAIL_FROM, APP_PASSWORD)
        yag.send(to=EMAIL_TO, subject=subject, contents=body_text)
    except Exception as e:
        print(f"failed to send email with error: {e}")
    
    
    
        