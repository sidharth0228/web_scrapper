"""
investor_matcher.py
===================
Investor Matching Demo Pipeline.
Matches investors to companies based on focus areas and regions using a weighted scoring algorithm.
"""

import os
import json
import config

EXPORTS_DIR = os.path.join(config.BASE_DIR, "exports")
DEFAULT_JSON = os.path.join(EXPORTS_DIR, "master_dataset.json")

def load_data(file_path: str = DEFAULT_JSON):
    if not os.path.exists(file_path):
        print(f"Error: Data file not found at {file_path}. Run scraper first.")
        return []
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def match_companies(investor_profile: dict, companies: list[dict]) -> list[dict]:
    """
    investor_profile = {
        "focus_tags": ["AI", "Robotics"],
        "target_region": "Europe",
        "target_type": "Startup"
    }
    """
    scored_matches = []
    
    for c in companies:
        score = 0
        reasons = []
        
        # 1. Tag matching (Heavy weight)
        company_tags = c.get("Technology Tags", "").lower()
        industry = c.get("Industry / Category", "").lower()
        desc = c.get("Short Description", "").lower()
        
        for focus in investor_profile.get("focus_tags", []):
            f_lower = focus.lower()
            if f_lower in company_tags or f_lower in industry or f_lower in desc:
                score += 50
                reasons.append(f"Matches focus: {focus}")
                
        # 2. Region matching (Medium weight)
        target_region = investor_profile.get("target_region", "").lower()
        if target_region:
            if target_region in c.get("Geographic Region", "").lower() or target_region in c.get("Location", "").lower():
                score += 30
                reasons.append(f"Matches region: {investor_profile['target_region']}")
                
        # 3. Type matching (Medium weight)
        target_type = investor_profile.get("target_type", "").lower()
        if target_type:
            if target_type == c.get("Company Type", "").lower():
                score += 20
                reasons.append(f"Matches type: {investor_profile['target_type']}")
                
        if score > 0:
            match_record = c.copy()
            match_record["Match Score"] = score
            match_record["Match Reasons"] = " | ".join(reasons)
            scored_matches.append(match_record)
            
    # Sort by descending score
    scored_matches.sort(key=lambda x: x["Match Score"], reverse=True)
    return scored_matches

def demo_matching():
    data = load_data()
    if not data:
        return
        
    investor = {
        "focus_tags": ["AI", "Robotics"],
        "target_region": "Europe",
        "target_type": "Startup"
    }
    
    print(f"--- INVESTOR PROFILE ---")
    print(f"Focus: {', '.join(investor['focus_tags'])}")
    print(f"Region: {investor['target_region']}")
    print(f"Type: {investor['target_type']}")
    print("------------------------\n")
    
    print("Running matching algorithm...\n")
    matches = match_companies(investor, data)
    
    if not matches:
        print("No matches found.")
    else:
        print(f"Top 5 Matches (out of {len(matches)} total):")
        for m in matches[:5]:
            print(f"[{m['Match Score']} pts] {m['Company Name']} ({m['Location']})")
            print(f"  Industry: {m['Industry / Category']}")
            print(f"  Why: {m['Match Reasons']}\n")
            
if __name__ == "__main__":
    demo_matching()
