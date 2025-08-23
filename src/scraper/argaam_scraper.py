"""
Main scraper for Argaam Shariah Companies
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import json
from typing import List, Dict, Optional
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import config
from src.utils.logger import get_logger
from src.utils.arabic_utils import normalize_arabic_text

logger = get_logger()

class ArgaamShariahScraper:
    """Scraper for Argaam Shariah-compliant companies"""
    
    def __init__(self, headless: bool = True):
        """
        Initialize the scraper
        
        Args:
            headless (bool): Run browser in headless mode
        """
        self.headless = headless
        self.driver = None
        self.companies_data = []
        
    def setup_driver(self):
        """Setup Selenium WebDriver"""
        try:
            options = Options()
            if self.headless:
                options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            options.add_experimental_option('excludeSwitches', ['enable-logging'])
            
            # Use webdriver-manager to automatically download and manage ChromeDriver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            
            logger.info("WebDriver setup completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup WebDriver: {str(e)}")
            return False
    
    def close_driver(self):
        """Close the WebDriver"""
        if self.driver:
            self.driver.quit()
            logger.info("WebDriver closed")
    
    def scrape_companies(self) -> List[Dict]:
        """
        Scrape all Shariah-compliant companies from Argaam
        
        Returns:
            List[Dict]: List of company data dictionaries
        """
        if not self.setup_driver():
            return []
        
        try:
            logger.info(f"Navigating to {config.SHARIAH_COMPANIES_URL}")
            self.driver.get(config.SHARIAH_COMPANIES_URL)
            
            # Wait for page to load
            wait = WebDriverWait(self.driver, config.SELENIUM_TIMEOUT)
            
            # Wait for the table or main content to load
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
            time.sleep(2)  # Additional wait for dynamic content
            
            # Get page source and parse with BeautifulSoup
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Extract companies from the table
            companies = self._extract_companies_from_page(soup)
            
            # Check for pagination and handle multiple pages
            companies.extend(self._handle_pagination())
            
            self.companies_data = companies
            logger.info(f"Successfully scraped {len(companies)} companies")
            
            return companies
            
        except Exception as e:
            logger.error(f"Error during scraping: {str(e)}")
            return []
        
        finally:
            self.close_driver()
    
    def _extract_companies_from_page(self, soup: BeautifulSoup) -> List[Dict]:
        """
        Extract company data from the current page
        
        Args:
            soup (BeautifulSoup): Parsed HTML content
            
        Returns:
            List[Dict]: List of company data
        """
        companies = []
        
        try:
            # Find all tables on the page
            tables = soup.find_all('table')
            
            for table in tables:
                rows = table.find_all('tr')
                
                for row in rows:
                    # Skip header rows
                    if row.find('th'):
                        continue
                    
                    cells = row.find_all('td')
                    if len(cells) >= 2:
                        company = self._parse_company_row(cells)
                        if company:
                            companies.append(company)
            
            logger.info(f"Extracted {len(companies)} companies from current page")
            
        except Exception as e:
            logger.error(f"Error extracting companies: {str(e)}")
        
        return companies
    
    def _parse_company_row(self, cells: List) -> Optional[Dict]:
        """
        Parse a single company row from the table
        
        Args:
            cells (List): List of table cells
            
        Returns:
            Optional[Dict]: Company data or None
        """
        try:
            # Extract text from cells
            cell_texts = [cell.get_text(strip=True) for cell in cells]
            
            # Basic structure based on the image
            company_data = {
                "timestamp": datetime.now().isoformat(),
                "company_code": "",
                "company_name": "",
                "ticker_symbol": "",
                "market": "",
                "shariah_board": "",
                "classification": "",
                "sector": "",
                "subsector": ""
            }
            
            # Parse based on cell position
            if len(cell_texts) >= 2:
                # First cell might contain company code
                if cell_texts[0] and cell_texts[0].isdigit():
                    company_data["company_code"] = cell_texts[0]
                    company_data["ticker_symbol"] = cell_texts[0]
                
                # Second cell contains company name
                if len(cell_texts) > 1:
                    company_data["company_name"] = normalize_arabic_text(cell_texts[1])
                
                # Determine market based on company code or other indicators
                company_data["market"] = self._determine_market(company_data)
                
                # Determine Shariah board (this would need additional logic)
                company_data["shariah_board"] = self._determine_shariah_board(company_data)
            
            return company_data if company_data["company_name"] else None
            
        except Exception as e:
            logger.error(f"Error parsing company row: {str(e)}")
            return None
    
    def _determine_market(self, company_data: Dict) -> str:
        """
        Determine if company is in TASI or Nomu market
        
        Args:
            company_data (Dict): Company data
            
        Returns:
            str: Market name in Arabic
        """
        # Logic to determine market
        # This would need to be refined based on actual page structure
        code = company_data.get("company_code", "")
        
        # Nomu companies typically have codes starting with 4
        if code.startswith("4"):
            return config.MARKETS["NOMU"]
        else:
            return config.MARKETS["TASI"]
    
    def _determine_shariah_board(self, company_data: Dict) -> str:
        """
        Determine the Shariah board for the company
        
        Args:
            company_data (Dict): Company data
            
        Returns:
            str: Shariah board name
        """
        # This would need to be extracted from the actual page
        # For now, returning a placeholder
        return "Unknown"
    
    def _handle_pagination(self) -> List[Dict]:
        """
        Handle pagination to get companies from all pages
        
        Returns:
            List[Dict]: Companies from additional pages
        """
        all_companies = []
        
        try:
            # Look for pagination controls
            pagination_selector = "a.pagination-link, button.next-page"
            next_buttons = self.driver.find_elements(By.CSS_SELECTOR, pagination_selector)
            
            page_num = 2
            while next_buttons and page_num <= 50:  # Safety limit
                try:
                    # Click next page
                    next_buttons[0].click()
                    time.sleep(2)  # Wait for page to load
                    
                    # Parse new page
                    soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                    companies = self._extract_companies_from_page(soup)
                    all_companies.extend(companies)
                    
                    # Check for more pages
                    next_buttons = self.driver.find_elements(By.CSS_SELECTOR, pagination_selector)
                    page_num += 1
                    
                except Exception as e:
                    logger.warning(f"Error handling page {page_num}: {str(e)}")
                    break
        
        except Exception as e:
            logger.warning(f"Pagination not found or error: {str(e)}")
        
        return all_companies
    
    def organize_by_market_and_board(self) -> Dict:
        """
        Organize companies by market and Shariah board
        
        Returns:
            Dict: Hierarchical structure of companies
        """
        organized_data = {
            "extraction_date": datetime.now().isoformat(),
            "total_companies": len(self.companies_data),
            "markets": {
                config.MARKETS["TASI"]: {
                    "total": 0,
                    "by_shariah_board": {}
                },
                config.MARKETS["NOMU"]: {
                    "total": 0,
                    "by_shariah_board": {}
                }
            }
        }
        
        for company in self.companies_data:
            market = company.get("market", config.MARKETS["TASI"])
            board = company.get("shariah_board", "Unknown")
            
            if market not in organized_data["markets"]:
                organized_data["markets"][market] = {
                    "total": 0,
                    "by_shariah_board": {}
                }
            
            if board not in organized_data["markets"][market]["by_shariah_board"]:
                organized_data["markets"][market]["by_shariah_board"][board] = []
            
            organized_data["markets"][market]["by_shariah_board"][board].append(company)
            organized_data["markets"][market]["total"] += 1
        
        return organized_data