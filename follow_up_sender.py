import csv
import time
import os
import subprocess
import json
import sys

# Load Configuration
def load_config():
    with open('config.json', 'r') as f:
        return json.load(f)

SENT_LOG = "sent_emails.txt"
FOLLOWUP_LOG = "followed_up.txt"

def load_sent_emails():
    if not os.path.exists(SENT_LOG):
        return set()
    with open(SENT_LOG, "r") as f:
        return set(line.strip() for line in f if line.strip())

def load_followed_up_emails():
    if not os.path.exists(FOLLOWUP_LOG):
        return set()
    with open(FOLLOWUP_LOG, "r") as f:
        return set(line.strip() for line in f if line.strip())

def log_followup(email):
    with open(FOLLOWUP_LOG, "a") as f:
        f.write(f"{email}\n")

def get_smart_greeting(email):
    # Try to guess name from email (e.g., john.doe@company.com)
    user_part = email.split('@')[0]
    if '.' in user_part:
        name = user_part.split('.')[0]
        return f"Hi {name.capitalize()},"
    return "Hi there,"

def get_followup_body(config, greeting):
    return f"""{greeting}

I wanted to quickly follow up on my previous email regarding the {config['job_title']} opportunity.

I remain very interested in the role and confident that my 5+ years of experience in SQL, Snowflake, and Power BI can bring immediate value to your team.

I’ve attached my resume again for your convenience.

Best regards,
{config['candidate_name']}
{config['job_title']}
📞 {config['phone']}
"""

def send_mac_mail_reply(recipient, subject, body, attachment_path):
    # Note: We add "Re:" to the subject to simulate a reply thread
    final_subject = f"Re: {subject}"
    
    apple_script = f'''
    tell application "Mail"
        set newMessage to make new outgoing message with properties {{subject:"{final_subject}", content:"{body}", visible:false}}
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
    resume_path = os.path.abspath(config['resume_filename'])

    if not os.path.exists(resume_path):
        print(f"❌ Resume not found at {resume_path}")
        return

    sent_emails = load_sent_emails()
    followed_up = load_followed_up_emails()
    
    # Identify candidates for follow-up (Sent but not Followed-up)
    to_contact = sent_emails - followed_up
    
    print(f"📊 Found {len(sent_emails)} total sent emails.")
    print(f"✅ Already followed up with {len(followed_up)} people.")
    print(f"🚀 Ready to follow up with {len(to_contact)} candidates.")
    
    if len(to_contact) == 0:
        print("No new candidates to follow up with.")
        return

    print("\n⚠️  WARNING: It is best practice to wait 3-5 days before following up.")
    # confirm = input("Type 'YES' to proceed sending follow-ups NOW: ")
    confirm = 'YES'
    
    if confirm.strip().upper() != 'YES':
        print("Cancelled.")
        return

    print(f"\n🚀 Starting Follow-Up Batch...")
    
    for email in to_contact:
        greeting = get_smart_greeting(email)
        body = get_followup_body(config, greeting)
        
        print(f"📧 Following up with {email}...", end="", flush=True)
        if send_mac_mail_reply(email, config['email_subject'], body, resume_path):
            print(" ✅ Sent")
            log_followup(email)
        else:
            print(" ❌ Failed")
        
        time.sleep(config['delay_seconds'])

if __name__ == "__main__":
    main()
