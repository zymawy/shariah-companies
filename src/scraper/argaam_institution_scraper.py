"""
Argaam Shariah Companies Scraper by Institution
This scraper iterates through each Shariah institution to get their certified companies
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import json
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import sys
import os
import platform
from functools import wraps
import re

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import config
from src.utils.logger import get_logger
from src.utils.arabic_utils import normalize_arabic_text

logger = get_logger()

class ArgaamInstitutionScraper:
    """Scraper for Argaam Shariah companies by institution"""
    
    def __init__(self, headless: bool = True, timeout: int = 30):
        """
        Initialize the scraper
        
        Args:
            headless (bool): Run browser in headless mode
            timeout (int): Default timeout for operations
        """
        self.headless = headless
        self.timeout = timeout
        self.driver = None
        self.companies_data = []
        self.scraping_stats = {
            "start_time": None,
            "end_time": None,
            "institutions_scraped": 0,
            "companies_found": 0,
            "companies_by_institution": {},
            "errors": []
        }
        
    def setup_driver(self) -> bool:
        """Setup Selenium WebDriver"""
        try:
            options = Options()
            
            # Enhanced options for stability
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            if self.headless:
                options.add_argument('--headless=new')
            
            # Detect platform and handle Apple Silicon
            system = platform.system()
            machine = platform.machine()
            
            logger.info(f"Detected platform: {system} {machine}")
            
            # Initialize driver based on platform
            if system == "Darwin" and machine == "arm64":
                # Apple Silicon Mac
                logger.info("Setting up ChromeDriver for Apple Silicon Mac...")
                chromedriver_path = "/opt/homebrew/bin/chromedriver"
                if os.path.exists(chromedriver_path):
                    logger.info(f"Using local ChromeDriver at {chromedriver_path}")
                    service = Service(chromedriver_path)
                else:
                    logger.info("Downloading ChromeDriver for ARM64...")
                    os.environ['WDM_ARCHITECTURE'] = 'arm64'
                    service = Service(ChromeDriverManager().install())
            else:
                logger.info("Setting up ChromeDriver using webdriver-manager...")
                service = Service(ChromeDriverManager().install())
            
            self.driver = webdriver.Chrome(service=service, options=options)
            self.driver.set_page_load_timeout(self.timeout)
            self.driver.implicitly_wait(10)
            
            logger.info("WebDriver setup completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup WebDriver: {str(e)}")
            return False
    
    def close_driver(self):
        """Close the WebDriver"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("WebDriver closed")
            except Exception as e:
                logger.warning(f"Error closing WebDriver: {str(e)}")
    
    def scrape_institution_companies(self, institution_id: int, institution_name: str, market_id: int = 3) -> List[Dict]:
        """
        Scrape companies for a specific institution and market
        
        Args:
            institution_id: The ID of the Shariah institution
            institution_name: The name of the institution
            market_id: The market ID (3 for TASI, 4 for Nomu, 0 for all)
            
        Returns:
            List of company dictionaries
        """
        companies = []
        
        try:
            # Construct URL for this institution and market
            url = f"{config.SHARIAH_COMPANIES_BASE_URL}/{institution_id}?marketid={market_id}"
            logger.info(f"Scraping {institution_name} from: {url}")
            
            # Navigate to the page - we're directly accessing the correct URL with institution and market IDs
            self.driver.get(url)
            time.sleep(3)  # Wait for page to load
            
            # Get page source and parse
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Find company table
            tables = soup.find_all('table')
            
            for table in tables:
                rows = table.find_all('tr')
                
                for row in rows:
                    # Skip header rows
                    if row.find('th'):
                        continue
                    
                    cells = row.find_all('td')
                    if cells:
                        company = self.extract_company_from_row(cells, institution_name, market_id)
                        if company:
                            companies.append(company)
            
            # Check for pagination
            companies.extend(self.handle_pagination(institution_name, market_id))
            
            logger.info(f"Found {len(companies)} companies for {institution_name}")
            
        except Exception as e:
            logger.error(f"Error scraping institution {institution_name}: {str(e)}")
            self.scraping_stats["errors"].append(f"Institution {institution_name}: {str(e)}")
        
        return companies
    
    def extract_company_from_row(self, cells: List, institution_name: str, market_id: int) -> Optional[Dict]:
        """Extract company data from table cells"""
        try:
            company_data = {
                "timestamp": datetime.now().isoformat(),
                "company_code": "",
                "company_name": "",
                "ticker_symbol": "",
                "market": "",
                "shariah_board": institution_name,
                "sector": "",
                "subsector": "",
                "classification": "شرعي",
                "purification_amount": None  # مبلغ التطهير للسهم الواحد (ريال)
            }
            
            # Extract data from cells
            for i, cell in enumerate(cells):
                cell_text = cell.get_text(strip=True)
                
                # First column is usually company code
                if i == 0 and cell_text.isdigit():
                    company_data["company_code"] = cell_text
                    company_data["ticker_symbol"] = cell_text
                # Second column is usually company name
                elif i == 1 and cell_text:
                    company_data["company_name"] = normalize_arabic_text(cell_text)
                # Check for purification amount (usually in later columns, contains decimal number)
                elif cell_text and '.' in cell_text:
                    try:
                        # Try to parse as float - likely purification amount
                        amount = float(cell_text)
                        if 0 <= amount <= 100:  # Reasonable range for purification amount per share
                            company_data["purification_amount"] = amount
                    except ValueError:
                        pass
                # Additional columns might have sector info
                elif cell_text and any(keyword in cell_text for keyword in ["العقار", "البنوك", "التأمين", "الصناعة"]):
                    company_data["sector"] = cell_text
            
            # If no code found in first cell, try to find it anywhere
            if not company_data["company_code"]:
                for cell in cells:
                    text = cell.get_text(strip=True)
                    # Look for 4-digit number
                    if text and text.isdigit() and len(text) == 4:
                        company_data["company_code"] = text
                        company_data["ticker_symbol"] = text
                        break
            
            # If no name found, look for Arabic text
            if not company_data["company_name"]:
                for cell in cells:
                    text = cell.get_text(strip=True)
                    if text and any('\u0600' <= c <= '\u06FF' for c in text):
                        company_data["company_name"] = normalize_arabic_text(text)
                        break
            
            # Determine market based on market_id or company code
            if market_id == 3:
                company_data["market"] = config.MARKETS["TASI"]
            elif market_id == 14:
                company_data["market"] = config.MARKETS["NOMU"]
            else:
                # Determine by company code
                if company_data["company_code"]:
                    code_int = int(company_data["company_code"])
                    if str(code_int).startswith("4") or code_int >= 9000:
                        company_data["market"] = config.MARKETS["NOMU"]
                    else:
                        company_data["market"] = config.MARKETS["TASI"]
            
            return company_data if company_data["company_name"] and company_data["company_code"] else None
            
        except Exception as e:
            logger.error(f"Error extracting company from row: {str(e)}")
            return None
    
    def handle_pagination(self, institution_name: str, market_id: int) -> List[Dict]:
        """Handle pagination for the current institution"""
        all_companies = []
        max_pages = 20
        current_page = 1
        
        while current_page < max_pages:
            try:
                # Look for next page button
                next_selectors = [
                    "a.next",
                    "a[rel='next']",
                    ".pagination a:contains('»')",
                    ".pagination a:contains('التالي')"
                ]
                
                next_element = None
                for selector in next_selectors:
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        if elements and elements[0].is_enabled():
                            next_element = elements[0]
                            break
                    except:
                        continue
                
                if not next_element:
                    break
                
                # Click next page
                self.driver.execute_script("arguments[0].scrollIntoView(true);", next_element)
                time.sleep(1)
                next_element.click()
                time.sleep(2)
                
                # Parse new page
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                tables = soup.find_all('table')
                
                for table in tables:
                    rows = table.find_all('tr')
                    for row in rows:
                        if not row.find('th'):
                            cells = row.find_all('td')
                            if cells:
                                company = self.extract_company_from_row(cells, institution_name, market_id)
                                if company:
                                    all_companies.append(company)
                
                current_page += 1
                
            except Exception as e:
                logger.debug(f"Pagination ended at page {current_page}: {str(e)}")
                break
        
        return all_companies
    
    def scrape_all_institutions(self, market_filter: str = "ALL") -> List[Dict]:
        """
        Scrape companies from all Shariah institutions
        
        Args:
            market_filter: "ALL", "TASI", or "NOMU"
            
        Returns:
            List of all companies with their institution assignments
        """
        self.scraping_stats["start_time"] = datetime.now()
        all_companies = []
        
        if not self.setup_driver():
            return []
        
        try:
            # Determine which market(s) to scrape
            if market_filter == "ALL":
                market_ids = [config.MARKET_IDS["TASI"], config.MARKET_IDS["NOMU"]]
            elif market_filter in config.MARKET_IDS:
                market_ids = [config.MARKET_IDS[market_filter]]
            else:
                market_ids = [config.MARKET_IDS["TASI"]]
            
            # Iterate through each institution
            for institution_id, institution_info in config.SHARIAH_INSTITUTIONS.items():
                institution_name = institution_info["name_ar"]
                
                logger.info(f"\n{'='*50}")
                logger.info(f"Scraping institution: {institution_name} (ID: {institution_id})")
                logger.info(f"{'='*50}")
                
                institution_companies = []
                
                # Scrape each market for this institution
                for market_id in market_ids:
                    market_name = "TASI" if market_id == 3 else "NOMU" if market_id == 14 else "ALL"
                    logger.info(f"Scraping {market_name} market...")
                    
                    companies = self.scrape_institution_companies(
                        institution_id, 
                        institution_name, 
                        market_id
                    )
                    institution_companies.extend(companies)
                
                # Update statistics
                self.scraping_stats["institutions_scraped"] += 1
                self.scraping_stats["companies_by_institution"][institution_name] = len(institution_companies)
                
                all_companies.extend(institution_companies)
                
                # Add a delay between institutions to avoid rate limiting
                time.sleep(2)
            
            # Remove duplicates (same company might be certified by multiple institutions)
            unique_companies = {}
            for company in all_companies:
                key = f"{company['company_code']}_{company['shariah_board']}"
                if key not in unique_companies:
                    unique_companies[key] = company
            
            self.companies_data = list(unique_companies.values())
            self.scraping_stats["companies_found"] = len(self.companies_data)
            self.scraping_stats["end_time"] = datetime.now()
            
            # Log final statistics
            self.log_statistics()
            
            return self.companies_data
            
        except Exception as e:
            logger.error(f"Fatal error during scraping: {str(e)}")
            self.scraping_stats["errors"].append(f"Fatal error: {str(e)}")
            return []
        
        finally:
            self.close_driver()
    
    def log_statistics(self):
        """Log scraping statistics"""
        duration = (self.scraping_stats["end_time"] - self.scraping_stats["start_time"]).seconds
        
        logger.info("\n" + "="*60)
        logger.info("SCRAPING COMPLETED")
        logger.info("="*60)
        logger.info(f"Duration: {duration} seconds")
        logger.info(f"Institutions scraped: {self.scraping_stats['institutions_scraped']}")
        logger.info(f"Total companies found: {self.scraping_stats['companies_found']}")
        
        logger.info("\nCompanies by Institution:")
        for institution, count in self.scraping_stats["companies_by_institution"].items():
            logger.info(f"  {institution}: {count} companies")
        
        # Market distribution
        market_dist = {}
        for company in self.companies_data:
            market = company.get("market", "Unknown")
            market_dist[market] = market_dist.get(market, 0) + 1
        
        logger.info("\nMarket Distribution:")
        for market, count in market_dist.items():
            logger.info(f"  {market}: {count} companies")
        
        if self.scraping_stats["errors"]:
            logger.warning(f"\nErrors encountered: {len(self.scraping_stats['errors'])}")
            for error in self.scraping_stats["errors"]:
                logger.warning(f"  - {error}")
    
    def get_statistics(self) -> Dict:
        """Get scraping statistics"""
        return self.scraping_stats