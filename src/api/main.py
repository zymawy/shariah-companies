"""
FastAPI application for Argaam Shariah Companies data
"""
from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from typing import Optional, List, Dict
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.database.models import DatabaseManager
from src.scheduler.scheduler import ScrapingScheduler
from src.scraper.enhanced_scraper import EnhancedArgaamScraper
from src.processors.classifier import CompanyClassifier
from src.utils.logger import get_logger
import config

logger = get_logger()

# Initialize FastAPI app
app = FastAPI(
    title="Argaam Shariah Companies API",
    description="API for accessing Shariah-compliant companies data from Saudi markets",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize scheduler (but don't start it automatically)
scheduler = ScrapingScheduler(interval_hours=config.UPDATE_INTERVAL_HOURS)

# Database manager (created per request)
def get_db():
    """Get database manager instance"""
    return DatabaseManager()

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Argaam Shariah Companies API",
        "version": "1.0.0",
        "documentation": "/docs",
        "endpoints": {
            "companies": "/api/v1/companies",
            "statistics": "/api/v1/statistics",
            "markets": "/api/v1/markets",
            "shariah_boards": "/api/v1/shariah-boards",
            "scrape": "/api/v1/scrape"
        }
    }

# Get all companies
@app.get("/api/v1/companies")
async def get_companies(
    market: Optional[str] = Query(None, description="Filter by market (تاسي or نمو)"),
    shariah_board: Optional[str] = Query(None, description="Filter by Shariah board"),
    sector: Optional[str] = Query(None, description="Filter by sector"),
    limit: int = Query(100, description="Maximum number of results"),
    offset: int = Query(0, description="Offset for pagination")
):
    """Get all companies with optional filters"""
    try:
        db = get_db()
        
        # Get companies from database
        companies = db.get_all_companies(market=market, shariah_board=shariah_board)
        
        # Apply sector filter if provided
        if sector:
            companies = [c for c in companies if c.sector == sector]
        
        # Apply pagination
        total = len(companies)
        companies = companies[offset:offset + limit]
        
        # Convert to dict
        companies_data = [company.to_dict() for company in companies]
        
        db.close()
        
        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "companies": companies_data
        }
        
    except Exception as e:
        logger.error(f"Error getting companies: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Get company by code
@app.get("/api/v1/companies/{company_code}")
async def get_company(company_code: str):
    """Get a specific company by code"""
    try:
        db = get_db()
        company = db.get_company_by_code(company_code)
        db.close()
        
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        
        return company.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting company {company_code}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Get statistics
@app.get("/api/v1/statistics")
async def get_statistics():
    """Get overall statistics"""
    try:
        db = get_db()
        stats = db.get_statistics()
        db.close()
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Get markets summary
@app.get("/api/v1/markets")
async def get_markets():
    """Get summary of companies by market"""
    try:
        db = get_db()
        stats = db.get_statistics()
        db.close()
        
        return {
            "markets": stats["by_market"],
            "last_update": stats["last_update"]
        }
        
    except Exception as e:
        logger.error(f"Error getting markets: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Get Shariah boards
@app.get("/api/v1/shariah-boards")
async def get_shariah_boards():
    """Get list of Shariah boards and their companies"""
    try:
        db = get_db()
        stats = db.get_statistics()
        db.close()
        
        return {
            "boards": stats["by_shariah_board"],
            "total_boards": len(stats["by_shariah_board"]),
            "last_update": stats["last_update"]
        }
        
    except Exception as e:
        logger.error(f"Error getting Shariah boards: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Get companies by Shariah board
@app.get("/api/v1/shariah-boards/{board_name}/companies")
async def get_board_companies(board_name: str):
    """Get companies certified by a specific Shariah board"""
    try:
        db = get_db()
        companies = db.get_all_companies(shariah_board=board_name)
        db.close()
        
        if not companies:
            raise HTTPException(status_code=404, detail="Shariah board not found or has no companies")
        
        return {
            "board": board_name,
            "total_companies": len(companies),
            "companies": [company.to_dict() for company in companies]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting board companies: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Trigger manual scrape
@app.post("/api/v1/scrape")
async def trigger_scrape(background_tasks: BackgroundTasks):
    """Trigger a manual scraping operation"""
    try:
        # Add scraping task to background
        background_tasks.add_task(run_scraper)
        
        return {
            "status": "started",
            "message": "Scraping task has been initiated in the background",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error triggering scrape: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Scheduler endpoints
@app.get("/api/v1/scheduler/status")
async def get_scheduler_status():
    """Get scheduler status"""
    try:
        return scheduler.get_status()
        
    except Exception as e:
        logger.error(f"Error getting scheduler status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/scheduler/start")
async def start_scheduler():
    """Start the scheduler"""
    try:
        scheduler.start()
        return {"status": "started", "message": "Scheduler has been started"}
        
    except Exception as e:
        logger.error(f"Error starting scheduler: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/scheduler/stop")
async def stop_scheduler():
    """Stop the scheduler"""
    try:
        scheduler.stop()
        return {"status": "stopped", "message": "Scheduler has been stopped"}
        
    except Exception as e:
        logger.error(f"Error stopping scheduler: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Export endpoints
@app.get("/api/v1/export/json")
async def export_json():
    """Export all companies as JSON"""
    try:
        from src.exporters.json_exporter import JSONExporter
        
        db = get_db()
        companies = db.get_all_companies()
        companies_data = [company.to_dict() for company in companies]
        db.close()
        
        exporter = JSONExporter()
        filepath = exporter.export_flat(companies_data, "api_export.json")
        
        return FileResponse(
            path=filepath,
            media_type="application/json",
            filename=f"shariah_companies_{datetime.now().strftime('%Y%m%d')}.json"
        )
        
    except Exception as e:
        logger.error(f"Error exporting JSON: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/export/excel")
async def export_excel():
    """Export all companies as Excel"""
    try:
        from src.exporters.excel_exporter import ExcelExporter
        
        db = get_db()
        companies = db.get_all_companies()
        companies_data = [company.to_dict() for company in companies]
        db.close()
        
        exporter = ExcelExporter()
        filepath = exporter.export_simple(companies_data, "api_export.xlsx")
        
        return FileResponse(
            path=filepath,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename=f"shariah_companies_{datetime.now().strftime('%Y%m%d')}.xlsx"
        )
        
    except Exception as e:
        logger.error(f"Error exporting Excel: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Helper function to run scraper
def run_scraper():
    """Run the scraper (for background tasks)"""
    try:
        scraper = EnhancedArgaamScraper(headless=True)
        companies = scraper.scrape_companies()
        
        if companies:
            db = DatabaseManager()
            for company_data in companies:
                if company_data.get('company_code'):
                    db.add_or_update_company(company_data)
            
            # Log activity
            db.log_scraping_activity(scraper.scraping_stats)
            db.close()
            
            logger.info(f"Background scraping completed. Found {len(companies)} companies")
        else:
            logger.warning("Background scraping completed with no companies found")
            
    except Exception as e:
        logger.error(f"Error in background scraping: {str(e)}")

# Run the API
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host=config.API_HOST,
        port=config.API_PORT,
        reload=False,
        log_level="info"
    )