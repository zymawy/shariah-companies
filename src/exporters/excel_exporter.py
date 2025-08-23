"""
Excel exporter for company data
"""
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

class ExcelExporter:
    """Export company data to Excel format"""
    
    def __init__(self, output_dir: Optional[Path] = None):
        """
        Initialize the Excel exporter
        
        Args:
            output_dir (Optional[Path]): Output directory for Excel files
        """
        self.output_dir = output_dir or config.EXPORTS_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def export_multi_sheet(self, companies: List[Dict], filename: Optional[str] = None) -> Path:
        """
        Export companies to Excel with multiple sheets (by market and Shariah board)
        
        Args:
            companies (List[Dict]): List of company data
            filename (Optional[str]): Output filename
            
        Returns:
            Path: Path to the exported file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"shariah_companies_{timestamp}.xlsx"
        
        filepath = self.output_dir / filename
        
        try:
            with pd.ExcelWriter(filepath, engine='xlsxwriter') as writer:
                # Get workbook and add formats
                workbook = writer.book
                header_format = workbook.add_format({
                    'bold': True,
                    'bg_color': '#D7E4BD',
                    'border': 1
                })
                
                # Sheet 1: All Companies
                df_all = pd.DataFrame(companies)
                df_all.to_excel(writer, sheet_name='جميع الشركات', index=False)
                
                # Sheet 2: TASI Companies
                tasi_companies = [c for c in companies if c.get("market") == config.MARKETS["TASI"]]
                if tasi_companies:
                    df_tasi = pd.DataFrame(tasi_companies)
                    df_tasi.to_excel(writer, sheet_name='تاسي', index=False)
                
                # Sheet 3: Nomu Companies
                nomu_companies = [c for c in companies if c.get("market") == config.MARKETS["NOMU"]]
                if nomu_companies:
                    df_nomu = pd.DataFrame(nomu_companies)
                    df_nomu.to_excel(writer, sheet_name='نمو', index=False)
                
                # Additional sheets by Shariah board
                boards = {}
                for company in companies:
                    board = company.get("shariah_board", "Unknown")
                    if board not in boards:
                        boards[board] = []
                    boards[board].append(company)
                
                for board, board_companies in boards.items():
                    # Limit sheet name to 31 characters (Excel limitation)
                    sheet_name = board[:31] if len(board) > 31 else board
                    df_board = pd.DataFrame(board_companies)
                    df_board.to_excel(writer, sheet_name=sheet_name, index=False)
                
                # Add summary sheet
                self._add_summary_sheet(writer, companies)
            
            logger.info(f"Exported {len(companies)} companies to Excel: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to export to Excel: {str(e)}")
            raise
    
    def _add_summary_sheet(self, writer: pd.ExcelWriter, companies: List[Dict]):
        """
        Add a summary sheet to the Excel file
        
        Args:
            writer (pd.ExcelWriter): Excel writer object
            companies (List[Dict]): List of company data
        """
        summary_data = {
            "الفئة": [],
            "العدد": []
        }
        
        # Total companies
        summary_data["الفئة"].append("إجمالي الشركات")
        summary_data["العدد"].append(len(companies))
        
        # By market
        markets = {}
        for company in companies:
            market = company.get("market", "Unknown")
            markets[market] = markets.get(market, 0) + 1
        
        for market, count in markets.items():
            summary_data["الفئة"].append(f"سوق {market}")
            summary_data["العدد"].append(count)
        
        # By Shariah board
        boards = {}
        for company in companies:
            board = company.get("shariah_board", "Unknown")
            boards[board] = boards.get(board, 0) + 1
        
        for board, count in boards.items():
            summary_data["الفئة"].append(board)
            summary_data["العدد"].append(count)
        
        df_summary = pd.DataFrame(summary_data)
        df_summary.to_excel(writer, sheet_name='ملخص', index=False)
    
    def export_simple(self, companies: List[Dict], filename: Optional[str] = None) -> Path:
        """
        Export companies to a simple Excel file
        
        Args:
            companies (List[Dict]): List of company data
            filename (Optional[str]): Output filename
            
        Returns:
            Path: Path to the exported file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"shariah_companies_simple_{timestamp}.xlsx"
        
        filepath = self.output_dir / filename
        
        try:
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
            
            # Export to Excel
            df.to_excel(filepath, index=False, engine='xlsxwriter')
            
            logger.info(f"Exported {len(companies)} companies to simple Excel: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to export simple Excel: {str(e)}")
            raise