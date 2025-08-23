"""
Enhanced Argaam Shariah Companies Scraper with robust error handling
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
from bs4 import BeautifulSoup
import time
import json
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import sys
import os
import platform
from functools import wraps

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import config
from src.utils.logger import get_logger
from src.utils.arabic_utils import normalize_arabic_text

logger = get_logger()

def retry_on_failure(max_attempts=3, delay=2):
    """Decorator for retrying failed operations"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        logger.error(f"Failed after {max_attempts} attempts: {str(e)}")
                        raise
                    logger.warning(f"Attempt {attempt + 1} failed, retrying... Error: {str(e)}")
                    time.sleep(delay)
            return None
        return wrapper
    return decorator

class EnhancedArgaamScraper:
    """Enhanced scraper with better error handling and retry logic"""
    
    def __init__(self, headless: bool = True, timeout: int = 30):
        """
        Initialize the enhanced scraper
        
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
            "pages_scraped": 0,
            "companies_found": 0,
            "errors": []
        }
        
    def setup_driver(self) -> bool:
        """Setup Selenium WebDriver with enhanced options"""
        try:
            options = Options()
            
            # Enhanced options for stability
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-web-security')
            options.add_argument('--disable-features=VizDisplayCompositor')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--start-maximized')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # User agent to appear more like a real browser
            options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            if self.headless:
                options.add_argument('--headless=new')  # Use new headless mode
            
            # Setup Chrome preferences
            prefs = {
                "profile.default_content_setting_values": {
                    "images": 2,  # Disable images for faster loading
                    "plugins": 2,
                    "popups": 2,
                    "geolocation": 2,
                    "notifications": 2,
                    "media_stream": 2,
                },
                "profile.managed_default_content_settings": {
                    "images": 2
                }
            }
            options.add_experimental_option("prefs", prefs)
            
            # Detect platform and handle Apple Silicon
            system = platform.system()
            machine = platform.machine()
            
            logger.info(f"Detected platform: {system} {machine}")
            
            # Initialize driver based on platform
            if system == "Darwin" and machine == "arm64":
                # Apple Silicon Mac
                logger.info("Setting up ChromeDriver for Apple Silicon Mac...")
                
                # Try to use local ChromeDriver first
                chromedriver_path = "/opt/homebrew/bin/chromedriver"
                if os.path.exists(chromedriver_path):
                    logger.info(f"Using local ChromeDriver at {chromedriver_path}")
                    service = Service(chromedriver_path)
                else:
                    # Use webdriver-manager with arm64 support
                    logger.info("Downloading ChromeDriver for ARM64...")
                    # Force ARM64 architecture
                    os.environ['WDM_ARCHITECTURE'] = 'arm64'
                    service = Service(ChromeDriverManager().install())
            else:
                # Intel Mac or other platforms
                logger.info("Setting up ChromeDriver using webdriver-manager...")
                service = Service(ChromeDriverManager().install())
            
            self.driver = webdriver.Chrome(service=service, options=options)
            
            # Set timeouts
            self.driver.set_page_load_timeout(self.timeout)
            self.driver.implicitly_wait(10)
            
            logger.info("WebDriver setup completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup WebDriver: {str(e)}")
            logger.info("Trying alternative setup method...")
            
            # Try alternative setup
            try:
                return self.setup_driver_alternative()
            except Exception as alt_e:
                logger.error(f"Alternative setup also failed: {str(alt_e)}")
                self.scraping_stats["errors"].append(f"Driver setup failed: {str(e)}")
                return False
    
    def setup_driver_alternative(self) -> bool:
        """Alternative WebDriver setup method"""
        try:
            from selenium.webdriver.chrome.service import Service as ChromeService
            
            options = Options()
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            
            if self.headless:
                options.add_argument('--headless')
            
            # Try without webdriver-manager
            logger.info("Attempting to use system Chrome/ChromeDriver...")
            
            # For Apple Silicon Macs, try common installation paths
            if platform.system() == "Darwin" and platform.machine() == "arm64":
                possible_paths = [
                    "/opt/homebrew/bin/chromedriver",
                    "/usr/local/bin/chromedriver",
                    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
                ]
                
                for path in possible_paths:
                    if os.path.exists(path) and "chromedriver" in path:
                        logger.info(f"Found ChromeDriver at {path}")
                        service = ChromeService(executable_path=path)
                        self.driver = webdriver.Chrome(service=service, options=options)
                        logger.info("Alternative WebDriver setup successful")
                        return True
            
            # Try default Chrome without specific driver path
            self.driver = webdriver.Chrome(options=options)
            logger.info("WebDriver setup with system Chrome successful")
            return True
            
        except Exception as e:
            logger.error(f"Alternative WebDriver setup failed: {str(e)}")
            return False
    
    def close_driver(self):
        """Safely close the WebDriver"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("WebDriver closed successfully")
            except Exception as e:
                logger.warning(f"Error closing WebDriver: {str(e)}")
    
    @retry_on_failure(max_attempts=3, delay=2)
    def navigate_to_page(self, url: str) -> bool:
        """Navigate to a URL with retry logic"""
        try:
            self.driver.get(url)
            time.sleep(3)  # Allow page to stabilize
            return True
        except TimeoutException:
            logger.warning(f"Timeout navigating to {url}")
            self.driver.refresh()
            return False
        except Exception as e:
            logger.error(f"Error navigating to {url}: {str(e)}")
            raise
    
    def wait_for_element(self, by: By, value: str, timeout: int = None) -> Optional:
        """Wait for an element with custom timeout"""
        timeout = timeout or self.timeout
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            logger.warning(f"Element not found: {value}")
            return None
    
    def select_shariah_board_filter(self, board_name: str = None):
        """Select a specific Shariah board from the dropdown if available"""
        try:
            # Look for Shariah board dropdown/filter
            # Common selectors for dropdowns on Argaam
            dropdown_selectors = [
                "select[name*='shariah']",
                "select[name*='board']",
                "select#shariahBoard",
                "#shariah-filter",
                ".shariah-dropdown",
                "select.form-control"
            ]
            
            for selector in dropdown_selectors:
                try:
                    dropdown = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if dropdown:
                        select = Select(dropdown)
                        if board_name:
                            # Try to select by visible text
                            try:
                                select.select_by_visible_text(board_name)
                                logger.info(f"Selected Shariah board: {board_name}")
                            except:
                                # Try partial match
                                options = select.options
                                for option in options:
                                    if board_name in option.text:
                                        select.select_by_visible_text(option.text)
                                        logger.info(f"Selected Shariah board: {option.text}")
                                        break
                        else:
                            # Get all available options
                            options = [option.text for option in select.options]
                            logger.info(f"Available Shariah boards: {options}")
                            return options
                        time.sleep(2)  # Wait for page to update
                        return True
                except:
                    continue
            
            logger.info("No Shariah board dropdown found")
            return False
            
        except Exception as e:
            logger.warning(f"Could not select Shariah board filter: {str(e)}")
            return False
    
    def extract_company_data_from_row(self, row) -> Optional[Dict]:
        """Extract company data from a table row with enhanced parsing"""
        try:
            cells = row.find_all('td')
            if not cells:
                return None
            
            company_data = {
                "timestamp": datetime.now().isoformat(),
                "company_code": "",
                "company_name": "",
                "ticker_symbol": "",
                "market": "",
                "shariah_board": "",
                "sector": "",
                "subsector": "",
                "classification": "شرعي"
            }
            
            # Based on the image provided, the structure appears to be:
            # Column 0: Empty or checkbox
            # Column 1: Company Code/Ticker
            # Column 2: Company Name
            # Column 3: Shariah Board (might be in dropdown or separate column)
            
            # Try different column configurations based on table structure
            if len(cells) >= 2:
                # Check if first cell has the code
                first_cell_text = cells[0].get_text(strip=True)
                second_cell_text = cells[1].get_text(strip=True) if len(cells) > 1 else ""
                
                # Determine which cell has the company code
                if first_cell_text and first_cell_text.isdigit():
                    company_data["company_code"] = first_cell_text
                    company_data["ticker_symbol"] = first_cell_text
                    if second_cell_text:
                        company_data["company_name"] = normalize_arabic_text(second_cell_text)
                elif second_cell_text and second_cell_text.isdigit():
                    company_data["company_code"] = second_cell_text
                    company_data["ticker_symbol"] = second_cell_text
                    if len(cells) > 2:
                        company_data["company_name"] = normalize_arabic_text(cells[2].get_text(strip=True))
                else:
                    # Try to find the code and name in any cell
                    for i, cell in enumerate(cells):
                        cell_text = cell.get_text(strip=True)
                        if cell_text:
                            # Check if it's a company code (4 digits)
                            if cell_text.isdigit() and len(cell_text) == 4:
                                company_data["company_code"] = cell_text
                                company_data["ticker_symbol"] = cell_text
                            # Check if it's Arabic text (likely company name)
                            elif any('\u0600' <= c <= '\u06FF' for c in cell_text):
                                if not company_data["company_name"]:
                                    company_data["company_name"] = normalize_arabic_text(cell_text)
                                # Check for Shariah board names
                                for board_key, board_name in config.SHARIAH_BOARDS.items():
                                    if board_name in cell_text:
                                        company_data["shariah_board"] = board_name
                                        break
            
            # Try to extract Shariah board from the row
            # Look for specific patterns or known board names
            row_text = row.get_text()
            for board_key, board_name in config.SHARIAH_BOARDS.items():
                if board_name in row_text:
                    company_data["shariah_board"] = board_name
                    break
            
            # Also check for data attributes or hidden fields
            if not company_data["shariah_board"]:
                # Check for data attributes
                for cell in cells:
                    # Check for data attributes
                    data_board = cell.get('data-board') or cell.get('data-shariah')
                    if data_board:
                        company_data["shariah_board"] = data_board
                        break
                    
                    # Check for title attributes
                    title = cell.get('title')
                    if title:
                        for board_key, board_name in config.SHARIAH_BOARDS.items():
                            if board_name in title:
                                company_data["shariah_board"] = board_name
                                break
            
            # Determine market based on code
            if company_data["company_code"]:
                code_int = int(company_data["company_code"])
                # Nomu market codes typically start with 4 or are above 9000
                if str(code_int).startswith("4") or code_int >= 9000:
                    company_data["market"] = config.MARKETS["NOMU"]
                else:
                    company_data["market"] = config.MARKETS["TASI"]
            
            # Set default Shariah board if not found
            if not company_data["shariah_board"]:
                company_data["shariah_board"] = "غير محدد"
            
            return company_data if company_data["company_name"] else None
            
        except Exception as e:
            logger.error(f"Error parsing company row: {str(e)}")
            return None
    
    def scrape_with_shariah_board_filter(self) -> List[Dict]:
        """Scrape companies by iterating through each Shariah board filter"""
        all_companies = []
        
        try:
            # First, try to get list of available Shariah boards
            boards = self.select_shariah_board_filter()
            
            if isinstance(boards, list) and len(boards) > 1:
                # We found a dropdown with multiple boards
                logger.info(f"Found {len(boards)} Shariah boards to iterate through")
                
                for board in boards:
                    if board and board != "الكل" and board != "All":  # Skip "All" option
                        logger.info(f"Scraping companies for board: {board}")
                        self.select_shariah_board_filter(board)
                        time.sleep(2)
                        
                        # Scrape companies for this board
                        companies = self.scrape_current_page()
                        
                        # Add the board name to each company
                        for company in companies:
                            company["shariah_board"] = board
                        
                        all_companies.extend(companies)
            else:
                # No dropdown found, scrape normally
                logger.info("No Shariah board filter found, scraping all companies")
                all_companies = self.scrape_current_page()
        
        except Exception as e:
            logger.error(f"Error in Shariah board filtering: {str(e)}")
        
        return all_companies
    
    def scrape_current_page(self) -> List[Dict]:
        """Scrape companies from the current page"""
        companies = []
        
        try:
            # Wait for content to load
            time.sleep(3)
            
            # Get page source
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Debug: Log the page structure
            tables = soup.find_all('table')
            logger.info(f"Found {len(tables)} tables on the page")
            
            for table_idx, table in enumerate(tables):
                # Look for table with company data
                rows = table.find_all('tr')
                logger.debug(f"Table {table_idx} has {len(rows)} rows")
                
                # Check if this table has company data
                # Usually company tables have specific classes or many rows
                if len(rows) > 5:  # Likely a data table
                    for row_idx, row in enumerate(rows):
                        # Skip header rows
                        if row.find('th'):
                            # Log header structure for debugging
                            headers = [th.get_text(strip=True) for th in row.find_all('th')]
                            logger.debug(f"Headers: {headers}")
                            continue
                        
                        company = self.extract_company_data_from_row(row)
                        if company:
                            companies.append(company)
                            logger.debug(f"Extracted: Code={company['company_code']}, Name={company['company_name'][:30]}, Board={company['shariah_board']}")
            
            # If no companies found, try alternative parsing
            if not companies:
                logger.warning("No companies found with standard parsing, trying alternative methods")
                companies = self.alternative_parsing(soup)
            
            self.scraping_stats["pages_scraped"] += 1
            self.scraping_stats["companies_found"] += len(companies)
            
            logger.info(f"Extracted {len(companies)} companies from current page")
            
        except Exception as e:
            logger.error(f"Error scraping current page: {str(e)}")
            self.scraping_stats["errors"].append(f"Page scraping error: {str(e)}")
        
        return companies
    
    def alternative_parsing(self, soup) -> List[Dict]:
        """Alternative parsing method for different page structures"""
        companies = []
        
        try:
            # Look for company data in different structures
            # Try divs with specific classes
            company_divs = soup.find_all('div', class_=['company-row', 'company-item', 'stock-item'])
            
            for div in company_divs:
                company_data = {
                    "timestamp": datetime.now().isoformat(),
                    "company_code": "",
                    "company_name": "",
                    "ticker_symbol": "",
                    "market": "",
                    "shariah_board": "غير محدد",
                    "sector": "",
                    "subsector": "",
                    "classification": "شرعي"
                }
                
                # Extract text and look for patterns
                text = div.get_text()
                
                # Look for 4-digit codes
                import re
                code_match = re.search(r'\b\d{4}\b', text)
                if code_match:
                    company_data["company_code"] = code_match.group()
                    company_data["ticker_symbol"] = code_match.group()
                
                # Look for Arabic company names
                arabic_text = re.findall(r'[\u0600-\u06FF\s]+', text)
                if arabic_text:
                    company_data["company_name"] = normalize_arabic_text(arabic_text[0])
                
                # Check for Shariah board
                for board_key, board_name in config.SHARIAH_BOARDS.items():
                    if board_name in text:
                        company_data["shariah_board"] = board_name
                        break
                
                if company_data["company_name"] and company_data["company_code"]:
                    companies.append(company_data)
            
            # Also try to find links with company information
            if not companies:
                links = soup.find_all('a', href=True)
                for link in links:
                    if '/company/' in link['href'] or 'stock' in link['href']:
                        text = link.get_text(strip=True)
                        # Parse the link text for company info
                        if text and any('\u0600' <= c <= '\u06FF' for c in text):
                            # This might be a company name
                            company_data = {
                                "timestamp": datetime.now().isoformat(),
                                "company_name": normalize_arabic_text(text),
                                "shariah_board": "غير محدد",
                                "classification": "شرعي"
                            }
                            
                            # Try to extract code from href
                            import re
                            code_match = re.search(r'/(\d{4})/', link['href'])
                            if code_match:
                                company_data["company_code"] = code_match.group(1)
                                company_data["ticker_symbol"] = code_match.group(1)
                            
                            if company_data.get("company_code"):
                                companies.append(company_data)
        
        except Exception as e:
            logger.error(f"Error in alternative parsing: {str(e)}")
        
        return companies
    
    def handle_pagination(self) -> List[Dict]:
        """Handle pagination with improved navigation"""
        all_companies = []
        max_pages = 50  # Safety limit
        current_page = 1
        
        while current_page < max_pages:
            try:
                # Look for next page button/link
                next_selectors = [
                    "a[rel='next']",
                    "a.next-page",
                    "button.next",
                    "li.pagination-next a",
                    "a:contains('التالي')",
                    "a:contains('»')",
                    ".pagination a:last-child",
                    "ul.pagination li:last-child a"
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
                    logger.info(f"No more pages found after page {current_page}")
                    break
                
                # Click next page
                self.driver.execute_script("arguments[0].scrollIntoView(true);", next_element)
                time.sleep(1)
                next_element.click()
                time.sleep(3)  # Wait for page to load
                
                # Scrape the new page
                companies = self.scrape_current_page()
                all_companies.extend(companies)
                
                current_page += 1
                logger.info(f"Moved to page {current_page}")
                
            except Exception as e:
                logger.warning(f"Pagination ended at page {current_page}: {str(e)}")
                break
        
        return all_companies
    
    def scrape_companies(self) -> List[Dict]:
        """Main method to scrape all companies with comprehensive error handling"""
        self.scraping_stats["start_time"] = datetime.now()
        
        if not self.setup_driver():
            return []
        
        try:
            logger.info(f"Starting scraping from {config.SHARIAH_COMPANIES_URL}")
            
            # Navigate to the main page
            if not self.navigate_to_page(config.SHARIAH_COMPANIES_URL):
                logger.error("Failed to navigate to main page")
                return []
            
            # Wait for initial content
            time.sleep(3)
            
            # Check if there's a Shariah board filter and use it
            companies = self.scrape_with_shariah_board_filter()
            
            # If no companies found with filter, try regular scraping
            if not companies:
                logger.info("Trying regular scraping without filters")
                
                # Scrape first page
                companies = self.scrape_current_page()
                
                # Handle pagination
                additional_companies = self.handle_pagination()
                companies.extend(additional_companies)
            
            self.companies_data = companies
            self.scraping_stats["end_time"] = datetime.now()
            
            # Log statistics
            duration = (self.scraping_stats["end_time"] - self.scraping_stats["start_time"]).seconds
            logger.info(f"Scraping completed in {duration} seconds")
            logger.info(f"Total pages scraped: {self.scraping_stats['pages_scraped']}")
            logger.info(f"Total companies found: {self.scraping_stats['companies_found']}")
            
            # Log Shariah board distribution
            board_counts = {}
            for company in companies:
                board = company.get("shariah_board", "غير محدد")
                board_counts[board] = board_counts.get(board, 0) + 1
            
            logger.info("Shariah board distribution:")
            for board, count in board_counts.items():
                logger.info(f"  {board}: {count} companies")
            
            if self.scraping_stats["errors"]:
                logger.warning(f"Errors encountered: {len(self.scraping_stats['errors'])}")
                for error in self.scraping_stats["errors"]:
                    logger.warning(f"  - {error}")
            
            return companies
            
        except Exception as e:
            logger.error(f"Fatal error during scraping: {str(e)}")
            self.scraping_stats["errors"].append(f"Fatal error: {str(e)}")
            return []
        
        finally:
            self.close_driver()
    
    def get_statistics(self) -> Dict:
        """Get scraping statistics"""
        return self.scraping_stats
    
    def validate_data(self) -> Tuple[bool, List[str]]:
        """Validate scraped data for completeness and accuracy"""
        issues = []
        
        for i, company in enumerate(self.companies_data):
            if not company.get("company_name"):
                issues.append(f"Company at index {i} has no name")
            
            if not company.get("company_code"):
                issues.append(f"Company '{company.get('company_name', 'Unknown')}' has no code")
            
            if not company.get("market"):
                issues.append(f"Company '{company.get('company_name', 'Unknown')}' has no market assigned")
            
            if company.get("shariah_board") == "غير محدد":
                issues.append(f"Company '{company.get('company_name', 'Unknown')}' has no Shariah board identified")
        
        is_valid = len(issues) == 0
        
        if is_valid:
            logger.info("Data validation passed")
        else:
            logger.warning(f"Data validation found {len(issues)} issues")
        
        return is_valid, issues