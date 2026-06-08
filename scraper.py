"""
scraper.py
==========
Main entry point for the Startup & Manufacturer Directory Scraper (BI Platform).
This orchestrates the scraping process based on the configured DATA_SOURCE.
"""

import sys
import config
from core import MockDirectoryScraper, WikipediaUnicornScraper
from enrichment import enrich_data
from exporter import export_data

def main():
    print("=====================================================")
    print(" Startup & Manufacturer Business Intelligence Engine")
    print("=====================================================")
    print(f"Configured Data Source: {config.DATA_SOURCE}")
    
    if config.DATA_SOURCE == "MOCK":
        scraper = MockDirectoryScraper()
    elif config.DATA_SOURCE == "WIKIPEDIA":
        scraper = WikipediaUnicornScraper()
    else:
        print(f"Unknown DATA_SOURCE '{config.DATA_SOURCE}' in config.py")
        sys.exit(1)
        
    scraper.run()
    
    # Extract raw records
    raw_records = scraper.get_records()
    print(f"Scraping complete. Collected {len(raw_records)} raw records.")
    
    if raw_records:
        # Phase 2: Business Intelligence Enrichment
        print("Enriching data with Business Intelligence tags...")
        enriched_records = enrich_data(raw_records)
        
        # Phase 6: Export System
        print("Exporting enriched data...")
        export_data(enriched_records)
        
    print("Pipeline execution finished successfully.")

if __name__ == "__main__":
    main()
