"""
core/wiki_scraper.py
====================
Concrete scraper targeting Wikipedia's List of unicorn startup companies.
This fulfills Phase 1: Real Data Integration.

Inherits BaseScraper and implements:
  - parse_page()  — extracts companies from the wikipedia table
  - run()         — single page execution
"""

from bs4 import BeautifulSoup
from core.base_scraper import BaseScraper
import config

class WikipediaUnicornScraper(BaseScraper):
    """
    Scrapes the Wikipedia List of unicorn startup companies.
    Data source: https://en.wikipedia.org/wiki/List_of_unicorn_startup_companies
    """
    
    SOURCE_NAME = "WikipediaUnicorns"
    
    def parse_page(self, html_content: str) -> list[dict]:
        if not html_content:
            return []
            
        soup = BeautifulSoup(html_content, "html.parser")
        records = []
        
        # Find the first wikitable which usually contains the list
        table = soup.find("table", class_="wikitable")
        if not table:
            self.logger.warning("Could not find the wikitable on the Wikipedia page.")
            return records
            
        rows = table.find_all("tr")
        
        # Typically Wikipedia tables have headers in the first row(s)
        # Assuming columns: Company, Valuation, Date, Country, City, Industry, ...
        # We will dynamically map headers if possible, or use standard index.
        headers = []
        if rows:
            headers = [th.get_text(strip=True).lower() for th in rows[0].find_all(["th", "td"])]
            
        company_idx = -1
        country_idx = -1
        industry_idx = -1
        
        for i, header in enumerate(headers):
            if "company" in header:
                company_idx = i
            elif "country" in header:
                country_idx = i
            elif "industry" in header:
                industry_idx = i
                
        # Fallback if headers change slightly
        if company_idx == -1: company_idx = 0
        if country_idx == -1: country_idx = 3
        if industry_idx == -1: industry_idx = 5
            
        for row in rows[1:]:
            cells = row.find_all(["td", "th"])
            if len(cells) > max(company_idx, country_idx, industry_idx):
                name = cells[company_idx].get_text(strip=True)
                location = cells[country_idx].get_text(strip=True)
                industry = cells[industry_idx].get_text(strip=True)
                
                # Extract URL from the link if present
                website = "N/A"
                a_tag = cells[company_idx].find("a")
                if a_tag and "href" in a_tag.attrs:
                    href = a_tag["href"]
                    if href.startswith("/wiki/"):
                        website = f"https://en.wikipedia.org{href}"
                    else:
                        website = href
                        
                if name:
                    records.append({
                        "Company Name": name,
                        "Industry / Category": industry,
                        "Location": location,
                        "Website URL": website,
                        "Short Description": f"Unicorn startup from {location} operating in {industry}.",
                        "Data Source": self.SOURCE_NAME
                    })
                    
        return records

    def run(self) -> None:
        self.logger.info(f"[{self.SOURCE_NAME}] Starting scrape run.")
        
        html = self.fetch_page(config.WIKI_URL)
        if not html:
            self.logger.warning("No HTML received. Stopping.")
            return
            
        page_records = self.parse_page(html)
        self.logger.info(
            f"[{self.SOURCE_NAME}] Parsed {len(page_records)} unicorn startups."
        )
        self.collected_records.extend(page_records)
        
        self.logger.info(
            f"[{self.SOURCE_NAME}] Run complete. Total records collected: {len(self.collected_records)}"
        )
