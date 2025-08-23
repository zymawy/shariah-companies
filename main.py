#!/usr/bin/env python3
"""
Main script to run the Argaam Shariah Companies Scraper
"""
import sys
from pathlib import Path
from datetime import datetime
import argparse

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.scraper.enhanced_scraper import EnhancedArgaamScraper
from src.scraper.argaam_institution_scraper import ArgaamInstitutionScraper
from src.processors.classifier import CompanyClassifier
from src.exporters.json_exporter import JSONExporter
from src.exporters.csv_exporter import CSVExporter
from src.exporters.excel_exporter import ExcelExporter
from src.utils.logger import get_logger
import config

logger = get_logger()

def main():
    """Main function to run the scraper"""
    
    parser = argparse.ArgumentParser(description='Argaam Shariah Companies Scraper')
    parser.add_argument(
        '--export-format', 
        choices=['json', 'csv', 'excel', 'all'],
        default='all',
        help='Export format for the scraped data'
    )
    parser.add_argument(
        '--market',
        choices=['تاسي', 'نمو', 'TASI', 'NOMU'],
        help='Filter by specific market'
    )
    parser.add_argument(
        '--shariah-board',
        help='Filter by specific Shariah board'
    )
    parser.add_argument(
        '--headless',
        action='store_true',
        default=True,
        help='Run browser in headless mode'
    )
    parser.add_argument(
        '--scraper',
        choices=['enhanced', 'institution'],
        default='institution',
        help='Which scraper to use (institution is recommended)'
    )
    
    args = parser.parse_args()
    
    logger.info("=" * 50)
    logger.info("Starting Argaam Shariah Companies Scraper")
    logger.info(f"Export format: {args.export_format}")
    logger.info("=" * 50)
    
    try:
        # Step 1: Initialize and run scraper
        logger.info("Step 1: Initializing scraper...")
        
        if args.scraper == 'institution':
            logger.info("Using institution-based scraper (recommended)")
            scraper = ArgaamInstitutionScraper(headless=args.headless)
            
            logger.info("Step 2: Scraping companies from Argaam by institution...")
            # Determine market filter
            if args.market:
                if args.market in ['تاسي', 'TASI']:
                    market_filter = 'TASI'
                elif args.market in ['نمو', 'NOMU']:
                    market_filter = 'NOMU'
                else:
                    market_filter = 'ALL'
            else:
                market_filter = 'ALL'
            
            companies = scraper.scrape_all_institutions(market_filter=market_filter)
        else:
            logger.info("Using enhanced scraper")
            scraper = EnhancedArgaamScraper(headless=args.headless)
            
            logger.info("Step 2: Scraping companies from Argaam...")
            companies = scraper.scrape_companies()
        
        if not companies:
            logger.error("No companies were scraped. Exiting.")
            return
        
        logger.info(f"Successfully scraped {len(companies)} companies")
        
        # Step 2: Classify companies
        logger.info("Step 3: Classifying companies...")
        classifier = CompanyClassifier()
        
        # Apply filters if specified
        if args.market:
            market_filter = config.MARKETS.get(args.market.upper(), args.market)
            companies = classifier.filter_companies(companies, market=market_filter)
            logger.info(f"Filtered to {len(companies)} companies in market: {market_filter}")
        
        if args.shariah_board:
            companies = classifier.filter_companies(companies, shariah_board=args.shariah_board)
            logger.info(f"Filtered to {len(companies)} companies with board: {args.shariah_board}")
        
        # Create hierarchical structure
        hierarchical_data = classifier.create_hierarchical_structure(companies)
        
        # Get statistics
        stats = classifier.get_statistics(companies)
        logger.info("Statistics:")
        logger.info(f"  Total companies: {stats['total_companies']}")
        logger.info(f"  Markets: {stats['by_market']}")
        logger.info(f"  Shariah boards: {len(stats['by_shariah_board'])} different boards")
        
        # Step 3: Export data
        logger.info("Step 4: Exporting data...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if args.export_format in ['json', 'all']:
            json_exporter = JSONExporter()
            
            # Export flat JSON
            json_file = json_exporter.export_flat(companies, f"companies_flat_{timestamp}.json")
            logger.info(f"Exported flat JSON: {json_file}")
            
            # Export hierarchical JSON
            hier_file = json_exporter.export_hierarchical(
                hierarchical_data, 
                f"companies_hierarchical_{timestamp}.json"
            )
            logger.info(f"Exported hierarchical JSON: {hier_file}")
            
            # Export by market
            market_file = json_exporter.export_by_market(
                companies,
                f"companies_by_market_{timestamp}.json"
            )
            logger.info(f"Exported by market JSON: {market_file}")
            
            # Export by Shariah board
            board_file = json_exporter.export_by_shariah_board(
                companies,
                f"companies_by_board_{timestamp}.json"
            )
            logger.info(f"Exported by Shariah board JSON: {board_file}")
        
        if args.export_format in ['csv', 'all']:
            csv_exporter = CSVExporter()
            csv_file = csv_exporter.export(companies, f"companies_{timestamp}.csv")
            logger.info(f"Exported CSV: {csv_file}")
            
            # Export separate CSVs by market
            market_files = csv_exporter.export_by_market(companies)
            for market, filepath in market_files.items():
                logger.info(f"Exported CSV for {market}: {filepath}")
        
        if args.export_format in ['excel', 'all']:
            excel_exporter = ExcelExporter()
            
            # Export multi-sheet Excel
            excel_file = excel_exporter.export_multi_sheet(
                companies, 
                f"companies_complete_{timestamp}.xlsx"
            )
            logger.info(f"Exported multi-sheet Excel: {excel_file}")
            
            # Export simple Excel
            simple_file = excel_exporter.export_simple(
                companies,
                f"companies_simple_{timestamp}.xlsx"
            )
            logger.info(f"Exported simple Excel: {simple_file}")
        
        logger.info("=" * 50)
        logger.info("Scraping completed successfully!")
        logger.info(f"All files exported to: {config.EXPORTS_DIR}")
        logger.info("=" * 50)
        
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    main()