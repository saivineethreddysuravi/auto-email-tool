import csv
import time
import os
import subprocess
import json

# Load Configuration
def load_config():
    with open('config.json', 'r') as f:
        return json.load(f)

SENT_LOG_FILE = "sent_emails.txt"

def load_sent_emails():
    if not os.path.exists(SENT_LOG_FILE):
        return set()
    with open(SENT_LOG_FILE, "r") as f:
        return set(line.strip() for line in f if line.strip())

def log_sent_email(email):
    with open(SENT_LOG_FILE, "a") as f:
        f.write(f"{email}\n")

def get_smart_greeting(email, company_name):
    user_part = email.split('@')[0]
    if '.' in user_part:
        name = user_part.split('.')[0]
        return f"Hi {name.capitalize()},"
    return f"Hi {company_name} Team,"

def get_body(config, greeting):
    return f"""{greeting}

I hope you’re doing well. I’m reaching out to explore {config['job_title']} opportunities within your team or current client openings.

    I have 5+ years of professional experience working across finance, payroll, and workforce analytics, with hands-on expertise in SQL, Snowflake, Power BI (DAX), Python, and Excel. I’ve built end-to-end dashboards, automated reporting workflows, and supported leadership teams with clear, decision-ready insights.
Most recently, I’ve been working on Power BI and Snowflake-based reporting solutions, owning data extraction, modeling, DAX development, and dashboard delivery. I’m actively seeking {config['job_title']} roles where I can contribute immediately.

I’ve included my resume and links below for quick reference:
• Resume: Attached
• Portfolio: {config['portfolio_url']}
• GitHub: {config['github_url']}
• LinkedIn: {config['linkedin_url']}

If there’s a role that aligns, I’d really appreciate the opportunity to connect. Even a short conversation would be valuable.

Thank you for your time, and I look forward to hearing from you.

Best regards,
{config['candidate_name']}
{config['job_title']}
📞 {config['phone']}
📧 {config['email']}
"""

def send_mac_mail(recipient, subject, body, attachment_path):
    apple_script = f'''
    tell application "Mail"
        set newMessage to make new outgoing message with properties {{subject:"{subject}", content:"{body}", visible:false}}
        tell newMessage
            make new to recipient at end of to recipients with properties {{address:"{recipient}"}}
            make new attachment with properties {{file name:POSIX file "{attachment_path}"}} at after the last paragraph
            send
        end tell
    end tell
    '''
    try:
        subprocess.run(["osascript", "-e", apple_script], check=True)
        return True
    except:
        return False

def main():
    if not os.path.exists('config.json'):
        print("❌ config.json not found.")
        return

    config = load_config()
    csv_file = "leads.csv"
    resume_path = os.path.abspath(config['resume_filename'])

    if not os.path.exists(resume_path):
        print(f"❌ Resume not found at {resume_path}")
        return

    sent_emails = load_sent_emails()
    print(f"🚀 Starting Bulk Send...")
    
    with open(csv_file, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            email = row['Email']
            company = row['Company']
            
            if email in sent_emails:
                continue
                
            greeting = get_smart_greeting(email, company)
            body = get_body(config, greeting)
            
            print(f"📧 Sending to {email}...", end="", flush=True)
            if send_mac_mail(email, config['email_subject'], body, resume_path):
                print(" ✅ Sent")
                log_sent_email(email)
            else:
                print(" ❌ Failed")
            
            time.sleep(config['delay_seconds'])

if __name__ == "__main__":
    main()
