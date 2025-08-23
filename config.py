"""
Configuration settings for Argaam Shariah Companies Scraper
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
EXPORTS_DIR = DATA_DIR / "exports"

# Create directories if they don't exist
for dir_path in [DATA_DIR, LOGS_DIR, EXPORTS_DIR, DATA_DIR / "raw", DATA_DIR / "processed"]:
    dir_path.mkdir(parents=True, exist_ok=True)

# Argaam URLs
ARGAAM_BASE_URL = "https://www.argaam.com"
# Updated URL pattern for Shariah companies by institution
SHARIAH_COMPANIES_BASE_URL = f"{ARGAAM_BASE_URL}/ar/company/shariahcompaniesbyinstitution"
# Old URL for reference
SHARIAH_COMPANIES_URL = f"{ARGAAM_BASE_URL}/ar/company/shariahcompanies/1/4/3"

# Markets
MARKETS = {
    "TASI": "تاسي",
    "NOMU": "نمو"
}

# Market IDs for URL construction
MARKET_IDS = {
    "ALL": 0,
    "TASI": 3,   # Main market
    "NOMU": 14   # Parallel market (نمو)
}

# Shariah Institutions with their IDs from the website
SHARIAH_INSTITUTIONS = {
    1: {
        "name_ar": "الراجحي المالية",
        "name_en": "Al Rajhi Financial",
        "id": 1
    },
    2: {
        "name_ar": "د.محمد بن سعود العصيمي",
        "name_en": "Dr.Muhammad bin Saud Al-Osaimi",
        "id": 2
    },
    3: {
        "name_ar": "تنمية للاستثمار",
        "name_en": "Development for Investment",
        "id": 3
    },
    6: {
        "name_ar": "البلاد المالية",
        "name_en": "Financial country",
        "id": 6
    }
}

# Legacy Shariah Boards mapping (for backward compatibility)
SHARIAH_BOARDS = {
    "ALRAJHI": "الراجحي المالية",
    "ALOSAIMI": "د.محمد بن سعود العصيمي",
    "TANMIYA": "تنمية للاستثمار",
    "ALBILAD": "البلاد المالية"
}

# Selenium Settings
SELENIUM_TIMEOUT = 30
SELENIUM_WAIT = 10
HEADLESS_MODE = os.getenv("HEADLESS_MODE", "True").lower() == "true"

# Export Settings
EXPORT_FORMATS = ["json", "csv", "excel", "sqlite"]
DEFAULT_EXPORT_FORMAT = "json"

# API Settings
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", 8000))

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"

# Database
DATABASE_URL = f"sqlite:///{DATA_DIR}/shariah_companies.db"

# Update Settings
UPDATE_INTERVAL_HOURS = int(os.getenv("UPDATE_INTERVAL_HOURS", 24))