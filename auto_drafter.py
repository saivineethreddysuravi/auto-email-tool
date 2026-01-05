import time
import re
import os
import pyperclip
import subprocess
import json

# Load Configuration
def load_config():
    with open('config.json', 'r') as f:
        return json.load(f)

def is_email(text):
    return re.match(r"[^@]+@[^@]+\.[^@]+", text)

def get_body(config, greeting):
    return f"""{greeting}

I hope you’re doing well. I’m reaching out to explore {config['job_title']} opportunities within your team or current client openings.

I have 4+ years of professional experience working across finance, payroll, and workforce analytics, with hands-on expertise in SQL, Snowflake, Power BI (DAX), Python, and Excel. I’ve built end-to-end dashboards, automated reporting workflows, and supported leadership teams with clear, decision-ready insights.

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

def create_mac_mail_draft(recipient, subject, body, attachment_path):
    apple_script = f'''
    tell application "Mail"
        set newMessage to make new outgoing message with properties {{subject:"{subject}", content:"{body}", visible:true}}
        tell newMessage
            make new to recipient at end of to recipients with properties {{address:"{recipient}"}}
            make new attachment with properties {{file name:POSIX file "{attachment_path}"}} at after the last paragraph
        end tell
        activate
    end tell
    '''
    try:
        subprocess.run(["osascript", "-e", apple_script], check=True)
        print(f"✅ Draft created for {recipient}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")

def main():
    if not os.path.exists('config.json'):
        print("❌ Error: config.json not found. Rename config.json.template to config.json and fill it out.")
        return

    config = load_config()
    resume_path = os.path.abspath(config['resume_filename'])

    print("🚀 Auto-Drafter (Portfolio Edition) Running...")
    print("📋 Copy an email address to launch a drafted email!")

    last_clipboard = ""
    try:
        while True:
            clipboard_content = pyperclip.paste().strip()
            if clipboard_content != last_clipboard:
                last_clipboard = clipboard_content
                if is_email(clipboard_content):
                    print(f"✨ Detected: {clipboard_content}")
                    create_mac_mail_draft(clipboard_content, config['email_subject'], get_body(config, "Hi,"), resume_path)
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping...")

if __name__ == "__main__":
    main()
