import os

# Centralized Web Scraper Configuration Settings

# --- DATA SOURCE SELECTION ---
# Available options: "MOCK", "WIKIPEDIA"
DATA_SOURCE = "MOCK"

# --- NETWORK & SERVER CONFIG ---
PORT = 8000
HOST = "localhost"
BASE_URL = f"http://{HOST}:{PORT}"
START_PAGE = "/page/1"
WIKI_URL = "https://en.wikipedia.org/wiki/List_of_unicorn_startup_companies"

# Simulated Error Endpoints (For testing scraper resilience)
SIMULATE_429_URL = f"{BASE_URL}/simulate-429"
SIMULATE_500_URL = f"{BASE_URL}/simulate-500"

# --- REQUEST PARAMETERS ---
# Standard browser User-Agent to bypass simple blocks
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
TIMEOUT_SECONDS = 5.0  # Timeout for establishing connection and reading response

# --- RETRY ENGINE PARAMETERS ---
# Exponential backoff parameters
MAX_RETRIES = 5          # Number of retry attempts for failed requests
BACKOFF_FACTOR = 1.0     # Delay multiplier (e.g., 1s, 2s, 4s, 8s, 16s)
RETRY_STATUS_CODES = [
    429,  # Too Many Requests (Rate Limiting)
    500,  # Internal Server Error (Server Downtime)
    502,  # Bad Gateway
    503,  # Service Unavailable
    504   # Gateway Timeout
]

# --- HTML CSS SELECTORS (For BeautifulSoup parsing) ---
# Separating selectors allows structural updates without modifying scraper logic
SELECTOR_COMPANY_CARD = "div.company-card"
SELECTOR_NAME = "h3.company-name"
SELECTOR_INDUSTRY = "span.company-industry"
SELECTOR_LOCATION = "span.company-location"
SELECTOR_WEBSITE = "a.company-website"
SELECTOR_DESCRIPTION = "p.company-description"
SELECTOR_NEXT_PAGE = "a.next-page"

# --- OUTPUT AND FILE LOGGING ---
# Absolute/Relative paths for directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
LOGS_DIR = os.path.join(BASE_DIR, "logs")

# Ensure directories exist
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

CSV_OUTPUT_PATH = os.path.join(OUTPUT_DIR, "company_directory.csv")
LOG_FILE_PATH = os.path.join(LOGS_DIR, "scraper.log")
