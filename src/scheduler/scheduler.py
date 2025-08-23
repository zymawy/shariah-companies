"""
Scheduler for automated scraping
"""
import schedule
import time
from datetime import datetime
import threading
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.scraper.enhanced_scraper import EnhancedArgaamScraper
from src.processors.classifier import CompanyClassifier
from src.exporters.json_exporter import JSONExporter
from src.exporters.excel_exporter import ExcelExporter
from src.database.models import DatabaseManager
from src.utils.logger import get_logger
import config

logger = get_logger()

class ScrapingScheduler:
    """Scheduler for automated scraping tasks"""
    
    def __init__(self, interval_hours=24):
        """
        Initialize the scheduler
        
        Args:
            interval_hours (int): Hours between scraping runs
        """
        self.interval_hours = interval_hours
        self.is_running = False
        self.thread = None
        self.last_run = None
        
    def scrape_and_save(self):
        """Main scraping task"""
        logger.info("=" * 50)
        logger.info("Starting scheduled scraping task")
        logger.info(f"Time: {datetime.now().isoformat()}")
        logger.info("=" * 50)
        
        try:
            # Initialize components
            scraper = EnhancedArgaamScraper(headless=True)
            classifier = CompanyClassifier()
            db_manager = DatabaseManager()
            json_exporter = JSONExporter()
            excel_exporter = ExcelExporter()
            
            # Step 1: Scrape companies
            logger.info("Step 1: Scraping companies from Argaam...")
            companies = scraper.scrape_companies()
            
            if not companies:
                logger.error("No companies scraped. Aborting task.")
                return
            
            logger.info(f"Successfully scraped {len(companies)} companies")
            
            # Step 2: Process and save to database
            logger.info("Step 2: Saving to database...")
            stats = {
                'start_time': scraper.scraping_stats['start_time'],
                'end_time': scraper.scraping_stats['end_time'],
                'companies_found': len(companies),
                'new_companies': 0,
                'updated_companies': 0,
                'errors': scraper.scraping_stats['errors']
            }
            
            active_codes = []
            for company_data in companies:
                if company_data.get('company_code'):
                    active_codes.append(company_data['company_code'])
                    
                    company, status = db_manager.add_or_update_company(company_data)
                    if status == 'created':
                        stats['new_companies'] += 1
                    elif status == 'updated':
                        stats['updated_companies'] += 1
            
            # Mark inactive companies
            db_manager.mark_inactive_companies(active_codes)
            
            # Log scraping activity
            db_manager.log_scraping_activity(stats)
            
            # Step 3: Export data
            logger.info("Step 3: Exporting data...")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Create hierarchical structure
            hierarchical_data = classifier.create_hierarchical_structure(companies)
            
            # Export to JSON
            json_file = json_exporter.export_hierarchical(
                hierarchical_data,
                f"scheduled_{timestamp}.json"
            )
            logger.info(f"Exported to JSON: {json_file}")
            
            # Export to Excel
            excel_file = excel_exporter.export_multi_sheet(
                companies,
                f"scheduled_{timestamp}.xlsx"
            )
            logger.info(f"Exported to Excel: {excel_file}")
            
            # Get and log statistics
            db_stats = db_manager.get_statistics()
            logger.info("Database Statistics:")
            logger.info(f"  Total companies: {db_stats['total_companies']}")
            logger.info(f"  TASI companies: {db_stats['by_market'].get(config.MARKETS['TASI'], 0)}")
            logger.info(f"  NOMU companies: {db_stats['by_market'].get(config.MARKETS['NOMU'], 0)}")
            logger.info(f"  New companies: {stats['new_companies']}")
            logger.info(f"  Updated companies: {stats['updated_companies']}")
            
            self.last_run = datetime.now()
            logger.info(f"Scheduled task completed successfully at {self.last_run}")
            
            # Close database connection
            db_manager.close()
            
        except Exception as e:
            logger.error(f"Error in scheduled task: {str(e)}")
            raise
    
    def run_immediately(self):
        """Run the scraping task immediately"""
        logger.info("Running scraping task immediately...")
        self.scrape_and_save()
    
    def start(self):
        """Start the scheduler"""
        if self.is_running:
            logger.warning("Scheduler is already running")
            return
        
        self.is_running = True
        
        # Schedule the job
        schedule.every(self.interval_hours).hours.do(self.scrape_and_save)
        
        # Run immediately on start
        self.run_immediately()
        
        # Start the scheduler in a separate thread
        def run_scheduler():
            while self.is_running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        
        self.thread = threading.Thread(target=run_scheduler, daemon=True)
        self.thread.start()
        
        logger.info(f"Scheduler started. Will run every {self.interval_hours} hours")
    
    def stop(self):
        """Stop the scheduler"""
        if not self.is_running:
            logger.warning("Scheduler is not running")
            return
        
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=5)
        
        schedule.clear()
        logger.info("Scheduler stopped")
    
    def get_next_run_time(self):
        """Get the next scheduled run time"""
        jobs = schedule.get_jobs()
        if jobs:
            return jobs[0].next_run
        return None
    
    def get_status(self):
        """Get scheduler status"""
        return {
            'is_running': self.is_running,
            'last_run': self.last_run.isoformat() if self.last_run else None,
            'next_run': self.get_next_run_time(),
            'interval_hours': self.interval_hours
        }

# Command-line interface for the scheduler
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Argaam Scraping Scheduler')
    parser.add_argument(
        '--interval',
        type=int,
        default=24,
        help='Hours between scraping runs (default: 24)'
    )
    parser.add_argument(
        '--run-once',
        action='store_true',
        help='Run once and exit'
    )
    
    args = parser.parse_args()
    
    scheduler = ScrapingScheduler(interval_hours=args.interval)
    
    if args.run_once:
        scheduler.run_immediately()
    else:
        try:
            scheduler.start()
            logger.info("Scheduler is running. Press Ctrl+C to stop.")
            
            # Keep the main thread alive
            while True:
                time.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.stop()
            logger.info("Scheduler stopped.")