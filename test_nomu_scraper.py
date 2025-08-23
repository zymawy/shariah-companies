#!/usr/bin/env python3
"""
Test script for NOMU market and purification amount extraction
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.scraper.argaam_institution_scraper import ArgaamInstitutionScraper
from src.utils.logger import get_logger
import config

logger = get_logger()

def test_nomu_scraper():
    """Test the institution-based scraper for NOMU market"""
    
    print("=" * 60)
    print("Testing NOMU Market Scraper")
    print("=" * 60)
    
    # Initialize scraper (set headless=False to see what's happening)
    scraper = ArgaamInstitutionScraper(headless=False)
    
    print("\nTesting NOMU market (ID: 14)")
    print("=" * 60)
    
    # Scrape NOMU market only
    companies = scraper.scrape_all_institutions(market_filter="NOMU")
    
    if companies:
        print(f"\n✓ Successfully scraped {len(companies)} companies from NOMU market")
        
        # Check for purification amounts
        companies_with_purification = [c for c in companies if c.get('purification_amount') is not None]
        
        if companies_with_purification:
            print(f"\n✓ Found {len(companies_with_purification)} companies with purification amounts")
            print("\nSample companies with purification amounts:")
            for i, company in enumerate(companies_with_purification[:5]):
                print(f"\n{i+1}. Company: {company.get('company_name', 'N/A')}")
                print(f"   Code: {company.get('company_code', 'N/A')}")
                print(f"   Market: {company.get('market', 'N/A')}")
                print(f"   Shariah Board: {company.get('shariah_board', 'N/A')}")
                print(f"   Purification Amount: {company.get('purification_amount', 'N/A')} SAR")
        else:
            print("\n⚠ No companies found with purification amounts")
        
        # Show sample data
        print("\n" + "=" * 60)
        print("Sample NOMU companies (first 5):")
        print("=" * 60)
        for i, company in enumerate(companies[:5]):
            print(f"\n{i+1}. Company: {company.get('company_name', 'N/A')}")
            print(f"   Code: {company.get('company_code', 'N/A')}")
            print(f"   Market: {company.get('market', 'N/A')}")
            print(f"   Shariah Board: {company.get('shariah_board', 'N/A')}")
            if company.get('purification_amount') is not None:
                print(f"   Purification Amount: {company.get('purification_amount')} SAR")
        
        # Show distribution by Shariah board
        board_dist = {}
        for company in companies:
            board = company.get('shariah_board', 'Unknown')
            board_dist[board] = board_dist.get(board, 0) + 1
        
        print("\n" + "=" * 60)
        print("NOMU Companies by Shariah Institution:")
        print("=" * 60)
        for board, count in board_dist.items():
            print(f"  {board}: {count} companies")
            
        # Show companies with purification by institution
        print("\n" + "=" * 60)
        print("Purification Amounts by Institution:")
        print("=" * 60)
        for institution_name in board_dist.keys():
            inst_companies = [c for c in companies if c.get('shariah_board') == institution_name]
            inst_with_purif = [c for c in inst_companies if c.get('purification_amount') is not None]
            if inst_with_purif:
                print(f"\n{institution_name}:")
                for company in inst_with_purif[:3]:  # Show first 3
                    print(f"  - {company.get('company_name')}: {company.get('purification_amount')} SAR")
            else:
                print(f"\n{institution_name}: No purification amounts")
    else:
        print("\n✗ No NOMU companies were scraped")
    
    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)

if __name__ == "__main__":
    test_nomu_scraper()