# Auto-Email Reachout Tool (macOS)

A productivity tool designed to streamline the job application process by automating email drafts and bulk outreach using Python and AppleScript.

## Features

- **Auto-Drafter:** Monitor the clipboard for email addresses. When an email is copied, the tool automatically generates a drafted email in the macOS Mail app with a pre-filled subject, body, and attached resume.
- **Bulk Sender:** Send personalized emails to a list of recruiters from a CSV file with built-in duplicate detection and safety delays.
- **Smart Greetings:** Automatically parses email addresses to greet recruiters by name or company.

## How It Works

This tool utilizes **AppleScript (osascript)** to interface directly with the macOS Mail application. This allows for seamless automation without needing to manage complex SMTP settings or App Passwords, while still supporting file attachments.

## Setup

1. **Clone the repository.**
2. **Configuration:**
   - Copy `config.json.template` to `config.json`.
   - Fill in your personal details (Name, Portfolio, Resume Path).
3. **Install Dependencies:**
   ```bash
   pip install pyperclip
   ```
4. **Run:**
   - For interactive mode: `python auto_drafter.py`
   - For bulk mode: `python bulk_sender.py`

## Technologies Used

- Python
- AppleScript
- macOS Mail API
- PyperClip (Clipboard Management)
