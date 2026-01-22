import pandas as pd
import os

MASTER_PATH = "/Users/vr/Desktop/Master_Outreach_List.csv"

def get_relevance_score(company_name):
    if not isinstance(company_name, str):
        return 0
        
    company_name = company_name.lower()
    
    # Tier 1: User's specific high-value targets (Finance & Healthcare)
    tier_1_keywords = [
        "health", "pharma", "medical", "care", "clinic", "hospital", "therapeutics",
        "bank", "financial", "capital", "insurance", "wealth", "asset", "invest", "credit", "finance"
    ]
    
    # Tier 2: Tech & Data (General Good Matches)
    tier_2_keywords = [
        "tech", "data", "analytics", "systems", "solutions", "software", "digital", "consulting", "group"
    ]
    
    score = 0
    for kw in tier_1_keywords:
        if kw in company_name:
            score += 10 # High weight for target sectors
            break # Count once per tier
            
    for kw in tier_2_keywords:
        if kw in company_name:
            score += 5
            break
            
    return score

def main():
    if not os.path.exists(MASTER_PATH):
        print("Master list not found.")
        return

    print("reading csv...")
    try:
        df = pd.read_csv(MASTER_PATH, on_bad_lines='skip')
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return
    
    print("Calculating relevance scores...")
    # Create a temporary column for sorting
    df['Relevance_Score'] = df['Company'].apply(get_relevance_score)
    
    # Sort logic:
    # 1. Status 'Pending' comes first (0), 'SENT' comes last (1)
    df['Status_Rank'] = df['Status'].apply(lambda x: 0 if str(x).lower().strip() == 'pending' else 1)
    
    # Sort by: Status (Pending first) -> Score (High to Low) -> Company Name (A-Z)
    df_sorted = df.sort_values(
        by=['Status_Rank', 'Relevance_Score', 'Company'], 
        ascending=[True, False, True]
    )
    
    # Drop temp columns
    df_sorted = df_sorted.drop(columns=['Relevance_Score', 'Status_Rank'])
    
    df_sorted.to_csv(MASTER_PATH, index=False)
    print(f"✅ Sorted {len(df_sorted)} leads. Top Finance/Healthcare leads are now first in line.")

if __name__ == "__main__":
    main()
