"""
core/base_scraper.py
====================
Abstract Base Class for all directory scrapers.

Every concrete scraper (Mock, Wikipedia, etc.) must inherit from BaseScraper
and implement the two abstract methods:
  - parse_page(html_content)  -> list[dict]
  - run()                     -> None

Shared infrastructure provided by BaseScraper:
  - Dual logging (console + file)
  - Session with exponential-backoff retry adapter
  - fetch_page(url)           -> str | None
  - validate_url(url_str)     -> str
"""

import logging
import sys
import urllib.parse
from abc import ABC, abstractmethod

import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

import config


class BaseScraper(ABC):
    """
    Abstract base class providing shared HTTP session management,
    logging, retry logic, and URL validation to all concrete scrapers.
    """

    # Subclasses override this to label records with their data source
    SOURCE_NAME: str = "Base"

    # ------------------------------------------------------------------ #
    # Initialisation
    # ------------------------------------------------------------------ #

    def __init__(self):
        self.collected_records: list[dict] = []
        self.session: requests.Session | None = None
        self.logger: logging.Logger = self._setup_logging()
        self._setup_session()
        self.logger.info(
            f"[{self.SOURCE_NAME}] Scraper initialised — "
            f"max_retries={config.MAX_RETRIES}, "
            f"backoff={config.BACKOFF_FACTOR}s"
        )

    # ------------------------------------------------------------------ #
    # Logging
    # ------------------------------------------------------------------ #

    def _setup_logging(self) -> logging.Logger:
        """
        Creates a named logger with two handlers:
          1. FileHandler  — DEBUG level, saves to logs/scraper.log
          2. StreamHandler — INFO level, prints to stdout
        """
        logger = logging.getLogger(self.__class__.__name__)
        logger.setLevel(logging.DEBUG)

        # Prevent duplicate handlers when the class is instantiated multiple times
        if logger.handlers:
            logger.handlers.clear()

        file_fmt = logging.Formatter(
            "%(asctime)s [%(levelname)s] [%(name)s:%(lineno)d] — %(message)s"
        )
        console_fmt = logging.Formatter(
            "%(asctime)s [%(levelname)s] — %(message)s", datefmt="%H:%M:%S"
        )

        # File handler — full trace
        fh = logging.FileHandler(config.LOG_FILE_PATH, encoding="utf-8")
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(file_fmt)
        logger.addHandler(fh)

        # Console handler — clean progress output
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.INFO)
        ch.setFormatter(console_fmt)
        logger.addHandler(ch)

        return logger

    # ------------------------------------------------------------------ #
    # HTTP session with retry adapter
    # ------------------------------------------------------------------ #

    def _setup_session(self) -> None:
        """
        Mounts an HTTPAdapter with a Retry strategy onto a requests.Session.

        Retry strategy (exponential backoff):
          Attempt 1: immediate
          Attempt 2: 1 × 2^0 =  1 s
          Attempt 3: 1 × 2^1 =  2 s
          Attempt 4: 1 × 2^2 =  4 s
          Attempt 5: 1 × 2^3 =  8 s

        The adapter retries automatically on any status code listed in
        config.RETRY_STATUS_CODES (429, 500, 502, 503, 504).
        """
        retry_strategy = Retry(
            total=config.MAX_RETRIES,
            backoff_factor=config.BACKOFF_FACTOR,
            status_forcelist=config.RETRY_STATUS_CODES,
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session = requests.Session()
        self.session.headers.update(config.HEADERS)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    # ------------------------------------------------------------------ #
    # Shared utilities
    # ------------------------------------------------------------------ #

    def fetch_page(self, url: str) -> str | None:
        """
        Performs an HTTP GET request using the resilient session.

        Args:
            url: Absolute URL to fetch.

        Returns:
            Raw HTML string on HTTP 200, otherwise None.
        """
        self.logger.info(f"GET {url}")
        try:
            response = self.session.get(url, timeout=config.TIMEOUT_SECONDS)
            self.logger.info(f"HTTP {response.status_code} ← {url}")

            if response.status_code == 200:
                return response.text
            elif response.status_code == 404:
                self.logger.warning(f"404 Not Found — {url}")
            else:
                self.logger.error(
                    f"Unhandled HTTP {response.status_code} — {url}"
                )
        except requests.exceptions.Timeout:
            self.logger.error(f"Timeout (>{config.TIMEOUT_SECONDS}s) — {url}")
        except requests.exceptions.ConnectionError:
            self.logger.error(f"Connection error — {url}")
        except requests.exceptions.RequestException as exc:
            self.logger.error(f"Request exception — {url}: {exc}")
        return None

    def validate_url(self, url_str: str) -> str:
        """
        Returns the URL if it has a valid scheme and network location,
        otherwise returns 'N/A'.
        """
        if not url_str or url_str.strip() in ("", "N/A"):
            return "N/A"
        try:
            parsed = urllib.parse.urlparse(url_str.strip())
            if parsed.scheme in ("http", "https") and parsed.netloc:
                return url_str.strip()
        except Exception:
            pass
        return "N/A"

    def get_records(self) -> list[dict]:
        """Returns all collected records after run() has been called."""
        return self.collected_records

    # ------------------------------------------------------------------ #
    # Abstract interface — subclasses must implement these
    # ------------------------------------------------------------------ #

    @abstractmethod
    def parse_page(self, html_content: str) -> list[dict]:
        """
        Parse raw HTML and return a list of company record dicts.

        Every dict must contain at minimum these keys:
            "Company Name", "Industry / Category", "Location",
            "Website URL", "Short Description", "Data Source"
        """

    @abstractmethod
    def run(self) -> None:
        """
        Execute the full scraping lifecycle and populate
        self.collected_records.
        """
