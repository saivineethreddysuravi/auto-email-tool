import os
import json
import pandas as pd
import requests
import re
from jobspy import scrape_jobs

def fetch_github_jobs():
    repos = [
        "https://raw.githubusercontent.com/jobs-jobr-pro/Data-Analyst-Jobs/main/README.md",
        "https://raw.githubusercontent.com/speedyapply/2026-SWE-College-Jobs/main/README.md",
        "https://raw.githubusercontent.com/SimplifyJobs/Summer2025-Internships/dev/README.md"
    ]
    
    all_companies = set()
    for url in repos:
        try:
            print(f"📡 Fetching from {url.split('/')[-3]}...")
            response = requests.get(url)
            response.raise_for_status()
            content = response.text
            
            # Match patterns like | **[Company]** | ... or | Company | ...
            # This regex is a bit more broad to handle different table formats
            matches = re.findall(r'\|\s*\*\*?\[?([^\]\*]+)\]?\(?.*?\)?\s*\*\*?\s*\|', content)
            for company in matches:
                clean_name = company.strip()
                if clean_name and clean_name not in ["Company", "---"]:
                    all_companies.add(clean_name)
        except Exception as e:
            print(f"⚠️ Error fetching from {url}: {e}")
    
    return list(all_companies)

def fetch_jobspy_jobs(search_term="Data Analyst", location="United States"):
    try:
        jobs = scrape_jobs(
            site_name=["indeed", "linkedin", "zip_recruiter", "glassdoor", "google"],
            search_term=search_term,
            location=location,
            results_wanted=30,
            hours_old=72,
            country_strictly_usa=True,
        )
        if jobs.empty:
            return []
        return jobs['company'].unique().tolist()
    except Exception as e:
        print(f"⚠️ Error fetching JobSpy jobs: {e}")
        return []

def generate_recruiter_emails(company_name):
    # Sanitize input
    if not isinstance(company_name, str):
        return []
        
    # Common recruiter email patterns
    clean_name = company_name.strip()
    if not clean_name:
        return []

    domain = clean_name.lower().replace(" ", "").replace("&", "") + ".com"
    patterns = [
        f"recruitment@{domain}",
        f"careers@{domain}",
        f"talent@{domain}",
        f"hiring@{domain}",
        f"tech-recruiting@{domain}",
        f"university-recruiting@{domain}"
    ]
    return patterns

def main():
    print("🔍 Fetching new job listings...")
    master_path = "/Users/vr/Desktop/Master_Outreach_List.csv"
    
    # 1. Fetch from GitHub
    github_companies = fetch_github_jobs()
    print(f"📈 Found {len(github_companies)} companies from GitHub lists.")
    
    # 2. Fetch from JobSpy
    target_sectors = "Finance Healthcare Banking Pharma Hospital"
    jobspy_companies = []
    for sector in target_sectors.split():
        print(f"🕵️ Searching JobSpy for Data Analyst in {sector}...")
        companies = fetch_jobspy_jobs(search_term=f"Data Analyst {sector}")
        jobspy_companies.extend(companies)
    
    all_companies = set(github_companies + jobspy_companies)
    
    # Load existing leads from Master List to avoid duplicates
    existing_emails = set()
    if os.path.exists(master_path):
        try:
            df_existing = pd.read_csv(master_path, on_bad_lines='skip')
            if not df_existing.empty:
                existing_emails = set(df_existing['Email'].dropna().unique())
        except Exception as e:
            print(f"⚠️ Error reading Master List: {e}")
    
    new_leads = []
    for company in all_companies:
        emails = generate_recruiter_emails(company)
        for email in emails:
            if email not in existing_emails:
                new_leads.append({
                    "Email": email, 
                    "Company": company,
                    "Job/Role": "Data Analyst",
                    "Status": "Pending",
                    "Key Tools": "SQL, Power BI, Snowflake, Excel",
                    "Job Focus/Needs": "Dashboards, Reporting, KPI Analysis"
                })
    
    if new_leads:
        df_new = pd.DataFrame(new_leads)
        # Append to Master List
        header = not os.path.exists(master_path)
        df_new.to_csv(master_path, mode='a', index=False, header=header)
        print(f"✅ Added {len(new_leads)} potential new leads to {master_path}")
    else:
        print("⏭️ No new unique leads found today.")

if __name__ == "__main__":
    main()
