"""
exporter.py
===========
Export system supporting CSV, Excel (.xlsx), and JSON.
Saves files to the exports/ directory.
"""

import os
import json
import pandas as pd
import config

EXPORTS_DIR = os.path.join(config.BASE_DIR, "exports")
os.makedirs(EXPORTS_DIR, exist_ok=True)

def export_data(records: list[dict], filename_base: str = "master_dataset"):
    """
    Exports a list of dicts to CSV, Excel, and JSON.
    """
    if not records:
        print("No records to export.")
        return
        
    df = pd.DataFrame(records)
    
    # Clean whitespace and handle NaN
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].astype(str).str.strip()
    df.fillna("N/A", inplace=True)
    
    # Paths
    csv_path = os.path.join(EXPORTS_DIR, f"{filename_base}.csv")
    xlsx_path = os.path.join(EXPORTS_DIR, f"{filename_base}.xlsx")
    json_path = os.path.join(EXPORTS_DIR, f"{filename_base}.json")
    
    # CSV Export
    df.to_csv(csv_path, index=False, encoding="utf-8")
    
    # Excel Export
    try:
        df.to_excel(xlsx_path, index=False)
    except Exception as e:
        print(f"Warning: Failed to export Excel (ensure openpyxl is installed). Error: {e}")
        
    # JSON Export
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(records, f, indent=4, ensure_ascii=False)
        
    print("============================================================")
    print(" DATA EXPORT COMPLETE                                       ")
    print(f" Exported {len(records)} records to {EXPORTS_DIR}")
    print(f" - {csv_path}")
    print(f" - {xlsx_path}")
    print(f" - {json_path}")
    print("============================================================")

    return df
