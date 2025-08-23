"""
Classifier for organizing companies by market and Shariah board
"""
from typing import List, Dict, Optional
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import config
from src.utils.logger import get_logger
from src.utils.arabic_utils import normalize_arabic_text

logger = get_logger()

class CompanyClassifier:
    """Classify companies by market and Shariah board"""
    
    def __init__(self):
        """Initialize the classifier"""
        self.markets = config.MARKETS
        self.shariah_boards = config.SHARIAH_BOARDS
        
    def classify_by_market(self, companies: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Classify companies by market (TASI or Nomu)
        
        Args:
            companies (List[Dict]): List of company data
            
        Returns:
            Dict[str, List[Dict]]: Companies organized by market
        """
        classified = {
            self.markets["TASI"]: [],
            self.markets["NOMU"]: []
        }
        
        for company in companies:
            market = company.get("market", self.markets["TASI"])
            if market in classified:
                classified[market].append(company)
            else:
                # Default to TASI if market is unknown
                classified[self.markets["TASI"]].append(company)
        
        logger.info(f"Classified {len(classified[self.markets['TASI']])} companies in TASI")
        logger.info(f"Classified {len(classified[self.markets['NOMU']])} companies in Nomu")
        
        return classified
    
    def classify_by_shariah_board(self, companies: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Classify companies by Shariah board
        
        Args:
            companies (List[Dict]): List of company data
            
        Returns:
            Dict[str, List[Dict]]: Companies organized by Shariah board
        """
        classified = {}
        
        for company in companies:
            board = company.get("shariah_board", "Unknown")
            board = normalize_arabic_text(board)
            
            if board not in classified:
                classified[board] = []
            
            classified[board].append(company)
        
        for board, companies in classified.items():
            logger.info(f"Classified {len(companies)} companies under {board}")
        
        return classified
    
    def create_hierarchical_structure(self, companies: List[Dict]) -> Dict:
        """
        Create a hierarchical structure: Market -> Shariah Board -> Companies
        
        Args:
            companies (List[Dict]): List of company data
            
        Returns:
            Dict: Hierarchical structure
        """
        structure = {
            "total_companies": len(companies),
            "markets": {}
        }
        
        # First classify by market
        by_market = self.classify_by_market(companies)
        
        # Then classify each market's companies by Shariah board
        for market, market_companies in by_market.items():
            structure["markets"][market] = {
                "total": len(market_companies),
                "by_shariah_board": self.classify_by_shariah_board(market_companies)
            }
        
        return structure
    
    def filter_companies(self, 
                        companies: List[Dict], 
                        market: Optional[str] = None,
                        shariah_board: Optional[str] = None) -> List[Dict]:
        """
        Filter companies by market and/or Shariah board
        
        Args:
            companies (List[Dict]): List of company data
            market (Optional[str]): Market to filter by
            shariah_board (Optional[str]): Shariah board to filter by
            
        Returns:
            List[Dict]: Filtered companies
        """
        filtered = companies
        
        if market:
            market = normalize_arabic_text(market)
            filtered = [c for c in filtered if normalize_arabic_text(c.get("market", "")) == market]
            logger.info(f"Filtered to {len(filtered)} companies in market: {market}")
        
        if shariah_board:
            shariah_board = normalize_arabic_text(shariah_board)
            filtered = [c for c in filtered if normalize_arabic_text(c.get("shariah_board", "")) == shariah_board]
            logger.info(f"Filtered to {len(filtered)} companies with Shariah board: {shariah_board}")
        
        return filtered
    
    def get_statistics(self, companies: List[Dict]) -> Dict:
        """
        Get statistics about the companies
        
        Args:
            companies (List[Dict]): List of company data
            
        Returns:
            Dict: Statistics
        """
        stats = {
            "total_companies": len(companies),
            "by_market": {},
            "by_shariah_board": {},
            "sectors": {}
        }
        
        # Count by market
        for company in companies:
            market = company.get("market", "Unknown")
            stats["by_market"][market] = stats["by_market"].get(market, 0) + 1
            
            # Count by Shariah board
            board = company.get("shariah_board", "Unknown")
            stats["by_shariah_board"][board] = stats["by_shariah_board"].get(board, 0) + 1
            
            # Count by sector
            sector = company.get("sector", "Unknown")
            if sector:
                stats["sectors"][sector] = stats["sectors"].get(sector, 0) + 1
        
        return stats