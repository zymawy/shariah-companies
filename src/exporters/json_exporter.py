"""
JSON exporter for company data
"""
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import config
from src.utils.logger import get_logger

logger = get_logger()

class JSONExporter:
    """Export company data to JSON format"""
    
    def __init__(self, output_dir: Optional[Path] = None):
        """
        Initialize the JSON exporter
        
        Args:
            output_dir (Optional[Path]): Output directory for JSON files
        """
        self.output_dir = output_dir or config.EXPORTS_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def export_flat(self, companies: List[Dict], filename: Optional[str] = None) -> Path:
        """
        Export companies as a flat JSON array
        
        Args:
            companies (List[Dict]): List of company data
            filename (Optional[str]): Output filename
            
        Returns:
            Path: Path to the exported file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"shariah_companies_flat_{timestamp}.json"
        
        filepath = self.output_dir / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(companies, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Exported {len(companies)} companies to {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to export to JSON: {str(e)}")
            raise
    
    def export_hierarchical(self, data: Dict, filename: Optional[str] = None) -> Path:
        """
        Export companies in hierarchical structure (Market -> Shariah Board -> Companies)
        
        Args:
            data (Dict): Hierarchical data structure
            filename (Optional[str]): Output filename
            
        Returns:
            Path: Path to the exported file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"shariah_companies_hierarchical_{timestamp}.json"
        
        filepath = self.output_dir / filename
        
        # Add metadata
        export_data = {
            "metadata": {
                "extraction_date": datetime.now().isoformat(),
                "source": "Argaam.com",
                "version": "1.0.0"
            },
            **data
        }
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Exported hierarchical data to {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to export hierarchical JSON: {str(e)}")
            raise
    
    def export_by_market(self, companies: List[Dict], filename: Optional[str] = None) -> Path:
        """
        Export companies grouped by market
        
        Args:
            companies (List[Dict]): List of company data
            filename (Optional[str]): Output filename
            
        Returns:
            Path: Path to the exported file
        """
        markets = {}
        for company in companies:
            market = company.get("market", "Unknown")
            if market not in markets:
                markets[market] = []
            markets[market].append(company)
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"companies_by_market_{timestamp}.json"
        
        filepath = self.output_dir / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(markets, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Exported companies by market to {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to export by market: {str(e)}")
            raise
    
    def export_by_shariah_board(self, companies: List[Dict], filename: Optional[str] = None) -> Path:
        """
        Export companies grouped by Shariah board
        
        Args:
            companies (List[Dict]): List of company data
            filename (Optional[str]): Output filename
            
        Returns:
            Path: Path to the exported file
        """
        boards = {}
        for company in companies:
            board = company.get("shariah_board", "Unknown")
            if board not in boards:
                boards[board] = []
            boards[board].append(company)
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"companies_by_shariah_board_{timestamp}.json"
        
        filepath = self.output_dir / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(boards, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Exported companies by Shariah board to {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to export by Shariah board: {str(e)}")
            raise