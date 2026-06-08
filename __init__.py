# core/__init__.py
# Exposes all scraper classes from the core package

from core.base_scraper import BaseScraper
from core.mock_scraper import MockDirectoryScraper
from core.wiki_scraper import WikipediaUnicornScraper

__all__ = ["BaseScraper", "MockDirectoryScraper", "WikipediaUnicornScraper"]
