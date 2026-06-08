"""
search_companies.py
===================
CLI Search Engine to query exported company data.
Allows searching by industry, location, and company type.
"""

import os
import json
import argparse
import config

EXPORTS_DIR = os.path.join(config.BASE_DIR, "exports")
DEFAULT_JSON = os.path.join(EXPORTS_DIR, "master_dataset.json")

def load_data(file_path: str = DEFAULT_JSON):
    if not os.path.exists(file_path):
        print(f"Error: Data file not found at {file_path}. Run scraper first.")
        return []
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def search(data, industry=None, location=None, company_type=None, tags=None):
    results = []
    for d in data:
        match = True
        if industry and industry.lower() not in d.get("Industry / Category", "").lower():
            match = False
        if location and location.lower() not in d.get("Location", "").lower() and location.lower() not in d.get("Geographic Region", "").lower():
            match = False
        if company_type and company_type.lower() not in d.get("Company Type", "").lower():
            match = False
        if tags and tags.lower() not in d.get("Technology Tags", "").lower():
            match = False
            
        if match:
            results.append(d)
    return results

def main():
    parser = argparse.ArgumentParser(description="Startup & Manufacturer Search Engine")
    parser.add_argument("--industry", type=str, help="Search by Industry (e.g., 'AI', 'Robotics')")
    parser.add_argument("--location", type=str, help="Search by Location (e.g., 'Germany', 'USA')")
    parser.add_argument("--type", type=str, help="Search by Company Type (e.g., 'Startup', 'Manufacturer')")
    parser.add_argument("--tags", type=str, help="Search by Tech Tags (e.g., 'FinTech')")
    
    args = parser.parse_args()
    
    if not any([args.industry, args.location, args.type, args.tags]):
        print("Please provide at least one search parameter. Use -h for help.")
        return
        
    data = load_data()
    if not data:
        return
        
    print(f"Searching {len(data)} records...")
    results = search(data, args.industry, args.location, args.type, args.tags)
    
    print("\n--- Search Results ---")
    if not results:
        print("No matching companies found.")
    else:
        for r in results:
            print(f"- {r.get('Company Name')} | {r.get('Company Type')} | {r.get('Location')} | {r.get('Industry / Category')}")
        print(f"\nTotal Matches: {len(results)}")

if __name__ == "__main__":
    main()
