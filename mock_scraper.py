"""
core/mock_scraper.py
====================
Concrete scraper targeting the local mock directory server (server.py).

Inherits BaseScraper and implements:
  - parse_page()  — extracts company cards from the mock HTML
  - run()         — paginates across all 10 pages + resilience lab tests
"""

import time
from bs4 import BeautifulSoup

import config
from core.base_scraper import BaseScraper


class MockDirectoryScraper(BaseScraper):
    """
    Scrapes the local mock directory served by server.py.

    Data source:  http://localhost:8000/page/{1-10}
    Records:      150 realistic startup & manufacturer listings
    Pagination:   Follows <a class="next-page"> links automatically
    """

    SOURCE_NAME = "MockDirectory"

    def parse_page(self, html_content: str) -> list[dict]:
        """
        Locates every <div class="company-card"> in the HTML, then extracts:
          - Company Name  : <h3 class="company-name">
          - Industry      : <span class="company-industry badge">
          - Location      : <span class="company-location badge">
          - Website URL   : href attr on <a class="company-website">
          - Description   : <p class="company-description">
        """
        if not html_content:
            return []

        soup = BeautifulSoup(html_content, "html.parser")

        # Select all company card containers on this page
        cards = soup.select(config.SELECTOR_COMPANY_CARD)
        self.logger.info(f"[{self.SOURCE_NAME}] Found {len(cards)} cards on page.")

        records = []
        for card in cards:
            name_el   = card.select_one(config.SELECTOR_NAME)
            ind_el    = card.select_one(config.SELECTOR_INDUSTRY)
            loc_el    = card.select_one(config.SELECTOR_LOCATION)
            web_el    = card.select_one(config.SELECTOR_WEBSITE)
            desc_el   = card.select_one(config.SELECTOR_DESCRIPTION)

            name    = name_el.get_text(strip=True)  if name_el  else "N/A"
            industry= ind_el.get_text(strip=True)   if ind_el   else "N/A"
            location= loc_el.get_text(strip=True)   if loc_el   else "N/A"
            website = self.validate_url(
                web_el["href"].strip() if web_el and web_el.has_attr("href") else "N/A"
            )
            desc    = desc_el.get_text(strip=True)  if desc_el  else "N/A"

            if name == "N/A":
                continue   # skip completely empty cards

            records.append({
                "Company Name"      : name,
                "Industry / Category": industry,
                "Location"          : location,
                "Website URL"       : website,
                "Short Description" : desc,
                "Data Source"       : self.SOURCE_NAME,
            })

        return records

    def _test_error_simulation(self) -> None:
        """
        Demonstrates retry resilience by calling both error endpoints.
        Logs whether the retry adapter successfully recovered.
        """
        self.logger.info("=" * 60)
        self.logger.info(" RESILIENCE LAB — Simulated Error Recovery")
        self.logger.info("=" * 60)

        tests = [
            ("Rate Limit (429)", config.SIMULATE_429_URL),
            ("Server Outage (500)", config.SIMULATE_500_URL),
        ]
        for label, url in tests:
            self.logger.info(f"Testing: {label}  →  {url}")
            html = self.fetch_page(url)
            status = "✓ RECOVERED" if html else "✗ FAILED"
            self.logger.info(f"  Result: {status}")

        self.logger.info("=" * 60)

    def run(self) -> None:
        """
        Full scraping lifecycle:
          1. Run error simulation tests
          2. Paginate through /page/1 … /page/10
          3. Parse each page and accumulate records
        """
        self.logger.info(f"[{self.SOURCE_NAME}] Starting scrape run.")

        # Optional resilience lab demo
        try:
            self._test_error_simulation()
        except Exception as exc:
            self.logger.warning(f"Resilience lab skipped — is server.py running? ({exc})")

        # --- Pagination loop ---
        current_path = config.START_PAGE          # "/page/1"
        page_num     = 1

        while current_path:
            full_url = f"{config.BASE_URL}{current_path}"
            self.logger.info(f"--- Page {page_num} ---")

            html = self.fetch_page(full_url)
            if not html:
                self.logger.warning(f"No HTML received for page {page_num}. Stopping.")
                break

            page_records = self.parse_page(html)
            self.logger.info(
                f"[{self.SOURCE_NAME}] Page {page_num}: {len(page_records)} records parsed."
            )
            self.collected_records.extend(page_records)

            # Detect next page link: <a class="next-page" href="/page/N">
            soup = BeautifulSoup(html, "html.parser")
            next_link = soup.select_one(config.SELECTOR_NEXT_PAGE)

            if next_link and next_link.get("href", "#") != "#":
                current_path = next_link["href"]
                page_num += 1
                time.sleep(0.3)   # polite crawl delay
            else:
                self.logger.info("Pagination complete — no further pages detected.")
                current_path = None

        self.logger.info(
            f"[{self.SOURCE_NAME}] Run complete. "
            f"Total records collected: {len(self.collected_records)}"
        )
