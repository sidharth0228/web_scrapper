"""
analytics.py
============
Analytics Dashboard Generator.
Creates charts and exports them to reports/ directory.
"""

import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import config

EXPORTS_DIR = os.path.join(config.BASE_DIR, "exports")
REPORTS_DIR = os.path.join(config.BASE_DIR, "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)
DEFAULT_JSON = os.path.join(EXPORTS_DIR, "master_dataset.json")

def load_data(file_path: str = DEFAULT_JSON):
    if not os.path.exists(file_path):
        print(f"Error: Data file not found at {file_path}. Run scraper first.")
        return []
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_reports():
    data = load_data()
    if not data:
        return
        
    df = pd.DataFrame(data)
    
    print("Generating Analytics Reports...")
    
    # 1. Companies by Geographic Region
    plt.figure(figsize=(10, 6))
    region_counts = df['Geographic Region'].value_counts()
    region_counts.plot(kind='bar', color='skyblue', edgecolor='black')
    plt.title('Companies by Geographic Region')
    plt.xlabel('Region')
    plt.ylabel('Count')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(REPORTS_DIR, 'region_distribution.png'))
    plt.close()
    
    # 2. Startup vs Manufacturer
    plt.figure(figsize=(8, 8))
    type_counts = df['Company Type'].value_counts()
    type_counts.plot(kind='pie', autopct='%1.1f%%', colors=['#ff9999','#66b3ff'], startangle=90)
    plt.title('Startup vs Manufacturer Distribution')
    plt.ylabel('')
    plt.tight_layout()
    plt.savefig(os.path.join(REPORTS_DIR, 'type_distribution.png'))
    plt.close()
    
    # 3. Top Business Categories
    plt.figure(figsize=(10, 6))
    cat_counts = df['Estimated Business Category'].value_counts()
    cat_counts.plot(kind='barh', color='lightgreen', edgecolor='black')
    plt.title('Business Category Distribution')
    plt.xlabel('Count')
    plt.ylabel('Category')
    plt.tight_layout()
    plt.savefig(os.path.join(REPORTS_DIR, 'category_distribution.png'))
    plt.close()
    
    print(f"Reports successfully generated in: {REPORTS_DIR}")
    print("- region_distribution.png")
    print("- type_distribution.png")
    print("- category_distribution.png")

if __name__ == "__main__":
    generate_reports()
