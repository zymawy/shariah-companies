"""
CSV exporter for company data
"""
import csv
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import config
from src.utils.logger import get_logger

logger = get_logger()

class CSVExporter:
    """Export company data to CSV format"""
    
    def __init__(self, output_dir: Optional[Path] = None):
        """
        Initialize the CSV exporter
        
        Args:
            output_dir (Optional[Path]): Output directory for CSV files
        """
        self.output_dir = output_dir or config.EXPORTS_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def export(self, companies: List[Dict], filename: Optional[str] = None) -> Path:
        """
        Export companies to CSV
        
        Args:
            companies (List[Dict]): List of company data
            filename (Optional[str]): Output filename
            
        Returns:
            Path: Path to the exported file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"shariah_companies_{timestamp}.csv"
        
        filepath = self.output_dir / filename
        
        try:
            # Convert to DataFrame for easier CSV export
            df = pd.DataFrame(companies)
            
            # Reorder columns for better readability
            column_order = [
                "company_code", "ticker_symbol", "company_name", 
                "market", "shariah_board", "sector", "subsector",
                "classification", "timestamp"
            ]
            
            # Only include columns that exist
            existing_columns = [col for col in column_order if col in df.columns]
            df = df[existing_columns]
            
            # Export to CSV
            df.to_csv(filepath, index=False, encoding='utf-8-sig')  # utf-8-sig for Excel compatibility
            
            logger.info(f"Exported {len(companies)} companies to CSV: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to export to CSV: {str(e)}")
            raise
    
    def export_by_market(self, companies: List[Dict], filename: Optional[str] = None) -> Dict[str, Path]:
        """
        Export companies to separate CSV files by market
        
        Args:
            companies (List[Dict]): List of company data
            filename (Optional[str]): Base filename
            
        Returns:
            Dict[str, Path]: Dictionary of market names to file paths
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        exported_files = {}
        
        # Group by market
        markets = {}
        for company in companies:
            market = company.get("market", "Unknown")
            if market not in markets:
                markets[market] = []
            markets[market].append(company)
        
        # Export each market to separate file
        for market, market_companies in markets.items():
            market_clean = market.replace(" ", "_").replace("/", "_")
            market_filename = f"companies_{market_clean}_{timestamp}.csv"
            filepath = self.export(market_companies, market_filename)
            exported_files[market] = filepath
        
        return exported_files