import csv
import time
import os
import subprocess
import json
import argparse

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
    # Specialized body for Data Analyst role
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
    # Escaping double quotes for AppleScript
    safe_body = body.replace('"', '\"')
    apple_script = f'''
    tell application "Mail"
        set newMessage to make new outgoing message with properties {{subject:"{subject}", content:"{safe_body}", visible:false}}
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
    except Exception as e:
        print(f" Error: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Send a morning batch of cold emails.")
    parser.add_argument("--limit", type=int, default=30, help="Number of emails to send.")
    args = parser.parse_args()

    if not os.path.exists('config.json'):
        print("❌ config.json not found.")
        return

    config = load_config()
    master_path = "/Users/vr/Desktop/Master_Outreach_List.csv"
    resume_path = os.path.abspath(config['resume_filename'])

    if not os.path.exists(resume_path):
        print(f"❌ Resume not found at {resume_path}")
        return

    if not os.path.exists(master_path):
        print(f"❌ {master_path} not found.")
        return

    # Load the Master List
    import pandas as pd
    try:
        df = pd.read_csv(master_path, on_bad_lines='skip')
    except Exception as e:
        print(f"❌ Error reading Master List: {e}")
        return

    sent_emails = load_sent_emails()
    
    # Identify companies that have ALREADY been contacted
    contacted_companies = set(df[df['Status'] == 'SENT']['Company'].unique())
    
    count = 0
    limit = args.limit

    print(f"🚀 Starting Morning Batch Outreach (Limit: {limit})...")
    print(f"ℹ️  Found {len(contacted_companies)} companies already contacted. Enforcing 1-email-per-company rule.")
    
    # Iterate through rows that are 'Pending' or not 'SENT'
    # We prioritize Pending but also check the sent_emails.txt for extra safety
    for index, row in df.iterrows():
        if count >= limit:
            break
            
        email = str(row['Email'])
        company = str(row['Company'])
        status = str(row.get('Status', 'Pending'))
        
        # Check if company was already contacted (globally or in this session)
        if company in contacted_companies:
            # Optional: Start skipping silently to reduce noise if many rows
            # print(f"⏭️  Skipping {email} ({company} already contacted).")
            continue

        if status == 'SENT' or email in sent_emails:
            continue
            
        greeting = get_smart_greeting(email, company)
        body = get_body(config, greeting)
        
        print(f"📧 [{count+1}/{limit}] Sending to {email} ({company})...", end="", flush=True)
        if send_mac_mail(email, config['email_subject'], body, resume_path):
            print(" ✅ Sent")
            log_sent_email(email)
            # Update the status in the dataframe
            df.at[index, 'Status'] = 'SENT'
            contacted_companies.add(company) # Mark company as contacted for this run
            count += 1
            # Save progress immediately to prevent data loss on interrupt
            df.to_csv(master_path, index=False)
        else:
            print(" ❌ Failed")
        
        time.sleep(config['delay_seconds'])

    # Save the updated Master List back to Desktop
    df.to_csv(master_path, index=False)
    print(f"🏁 Morning Batch Complete. Sent {count} emails. Master List updated.")

if __name__ == "__main__":
    main()
