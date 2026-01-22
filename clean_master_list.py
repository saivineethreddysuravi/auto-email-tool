import pandas as pd
import os
import re

master_path = "/Users/vr/Desktop/Master_Outreach_List.csv"
backup_path = "/Users/vr/Desktop/Master_Outreach_List_backup.csv"

def clean_list():
    if not os.path.exists(master_path):
        print(f"❌ Master list not found at {master_path}")
        return

    print(f"🔄 Reading {master_path}...")
    df = pd.read_csv(master_path, on_bad_lines='skip')
    initial_count = len(df)

    # 1. Backup
    df.to_csv(backup_path, index=False)
    print(f"💾 Backup created at {backup_path}")

    # 2. Basic Cleanup
    df = df.dropna(subset=['Email'])
    df['Email'] = df['Email'].str.strip()
    
    # 3. Valid Email Regex
    # Stricter regex: No commas, no double dots
    # The previous regex might have slipped if not applied correctly or if pandas regex behavior varied.
    # We will explicitly filter out common bad patterns first.
    
    # Filter out emails with commas or double dots
    df = df[~df['Email'].str.contains(r',|\.\.', regex=True, na=False)]
    
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    df = df[df['Email'].str.match(email_regex, na=False)]

    # 4. Remove Generic/Waste Emails
    # We keep 'recruiting', 'hr', 'careers', 'hiring' but remove 'info', 'support', 'admin', etc.
    waste_prefixes = ['info', 'support', 'admin', 'sales', 'help', 'contact', 'webmaster', 'test', 'office', 'marketing']
    waste_pattern = r'^(?:' + '|'.join(waste_prefixes) + r')@'
    df = df[~df['Email'].str.contains(waste_pattern, case=False, na=False)]

    # 5. Remove Free/Low-Quality Providers
    # Based on user feedback that these are 'waste of time'
    free_providers = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'icloud.com', 'aol.com', 'rediffmail.com', 'zoho.com']
    df = df[~df['Email'].str.split('@').str[-1].str.lower().isin(free_providers)]

    # 6. US Filter (Simple TLD and Keyword check)
    # Remove known non-US TLDs
    non_us_tlds = ['.in', '.uk', '.ca', '.au', '.pk', '.eu', '.de', '.fr']
    for tld in non_us_tlds:
        df = df[~df['Email'].str.lower().str.endswith(tld, na=False)]

    # 7. Deduplicate
    df = df.drop_duplicates(subset=['Email'])

    final_count = len(df)
    removed_count = initial_count - final_count

    # Save cleaned list
    df.to_csv(master_path, index=False)
    
    print(f"✅ Cleanup Complete!")
    print(f"📊 Initial: {initial_count}")
    print(f"📊 Removed: {removed_count}")
    print(f"📊 Final:   {final_count}")
    print(f"🚀 Master List updated at {master_path}")

if __name__ == "__main__":
    clean_list()
