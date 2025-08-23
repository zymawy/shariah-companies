#!/usr/bin/env python3
"""
Test script for the institution-based scraper
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.scraper.argaam_institution_scraper import ArgaamInstitutionScraper
from src.utils.logger import get_logger
import config

logger = get_logger()

def test_institution_scraper():
    """Test the institution-based scraper"""
    
    print("=" * 60)
    print("Testing Argaam Institution Scraper")
    print("=" * 60)
    
    # Initialize scraper (set headless=False to see what's happening)
    scraper = ArgaamInstitutionScraper(headless=False)
    
    print("\nAvailable Shariah Institutions:")
    for inst_id, inst_info in config.SHARIAH_INSTITUTIONS.items():
        print(f"  {inst_id}: {inst_info['name_ar']} ({inst_info['name_en']})")
    
    print("\n" + "=" * 60)
    print("Starting scraping process...")
    print("=" * 60)
    
    # Scrape all institutions for TASI market only (faster for testing)
    companies = scraper.scrape_all_institutions(market_filter="TASI")
    
    if companies:
        print(f"\n✓ Successfully scraped {len(companies)} companies")
        
        # Show sample data
        print("\nSample companies (first 5):")
        for i, company in enumerate(companies[:5]):
            print(f"\n{i+1}. Company: {company.get('company_name', 'N/A')}")
            print(f"   Code: {company.get('company_code', 'N/A')}")
            print(f"   Market: {company.get('market', 'N/A')}")
            print(f"   Shariah Board: {company.get('shariah_board', 'N/A')}")
        
        # Show distribution
        board_dist = {}
        for company in companies:
            board = company.get('shariah_board', 'Unknown')
            board_dist[board] = board_dist.get(board, 0) + 1
        
        print("\n" + "=" * 60)
        print("Companies by Shariah Institution:")
        print("=" * 60)
        for board, count in board_dist.items():
            print(f"  {board}: {count} companies")
    else:
        print("\n✗ No companies were scraped")
    
    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)

if __name__ == "__main__":
    test_institution_scraper()