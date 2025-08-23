"""
Test suite for the Argaam scraper
"""
import pytest
import sys
import os
from unittest.mock import MagicMock, patch
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scraper.enhanced_scraper import EnhancedArgaamScraper
from src.utils.arabic_utils import normalize_arabic_text, is_arabic

class TestArabicUtils:
    """Test Arabic text utilities"""
    
    def test_normalize_arabic_text(self):
        """Test Arabic text normalization"""
        # Test with diacritics
        text_with_diacritics = "الشَّرِكَةُ"
        normalized = normalize_arabic_text(text_with_diacritics)
        assert normalized == "الشركة"
        
        # Test with extra spaces
        text_with_spaces = "الشركة   الوطنية"
        normalized = normalize_arabic_text(text_with_spaces)
        assert normalized == "الشركة الوطنية"
        
        # Test empty string
        assert normalize_arabic_text("") == ""
        assert normalize_arabic_text(None) == None
    
    def test_is_arabic(self):
        """Test Arabic text detection"""
        assert is_arabic("الشركة") == True
        assert is_arabic("Company") == False
        assert is_arabic("الشركة Company") == True
        assert is_arabic("") == False
        assert is_arabic(None) == False

class TestEnhancedScraper:
    """Test the enhanced scraper"""
    
    def test_scraper_initialization(self):
        """Test scraper initialization"""
        scraper = EnhancedArgaamScraper(headless=True, timeout=30)
        
        assert scraper.headless == True
        assert scraper.timeout == 30
        assert scraper.driver == None
        assert scraper.companies_data == []
        assert scraper.scraping_stats["companies_found"] == 0
    
    @patch('src.scraper.enhanced_scraper.webdriver.Chrome')
    def test_setup_driver(self, mock_chrome):
        """Test WebDriver setup"""
        scraper = EnhancedArgaamScraper(headless=True)
        
        # Mock the Chrome driver
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver
        
        result = scraper.setup_driver()
        
        assert result == True
        assert scraper.driver is not None
    
    def test_extract_company_data_from_row(self):
        """Test extracting company data from a table row"""
        scraper = EnhancedArgaamScraper()
        
        # Create mock row with cells
        mock_row = MagicMock()
        mock_cell1 = MagicMock()
        mock_cell1.get_text.return_value = "9510"
        mock_cell2 = MagicMock()
        mock_cell2.get_text.return_value = "الشركة الوطنية للبناء والتسويق"
        
        mock_row.find_all.return_value = [mock_cell1, mock_cell2]
        
        company_data = scraper.extract_company_data_from_row(mock_row)
        
        assert company_data is not None
        assert company_data["company_code"] == "9510"
        assert company_data["ticker_symbol"] == "9510"
        assert "الشركة الوطنية" in company_data["company_name"]
        assert company_data["market"] in ["تاسي", "نمو"]
    
    def test_validate_data(self):
        """Test data validation"""
        scraper = EnhancedArgaamScraper()
        
        # Test with valid data
        scraper.companies_data = [
            {
                "company_code": "9510",
                "company_name": "Test Company",
                "market": "تاسي"
            }
        ]
        
        is_valid, issues = scraper.validate_data()
        assert is_valid == True
        assert len(issues) == 0
        
        # Test with invalid data
        scraper.companies_data = [
            {
                "company_code": "",
                "company_name": "Test Company",
                "market": "تاسي"
            },
            {
                "company_code": "1234",
                "company_name": "",
                "market": "نمو"
            }
        ]
        
        is_valid, issues = scraper.validate_data()
        assert is_valid == False
        assert len(issues) > 0

class TestClassifier:
    """Test the company classifier"""
    
    def test_classify_by_market(self):
        """Test market classification"""
        from src.processors.classifier import CompanyClassifier
        
        classifier = CompanyClassifier()
        
        companies = [
            {"company_code": "1111", "market": "تاسي"},
            {"company_code": "2222", "market": "تاسي"},
            {"company_code": "4444", "market": "نمو"},
        ]
        
        classified = classifier.classify_by_market(companies)
        
        assert len(classified["تاسي"]) == 2
        assert len(classified["نمو"]) == 1
    
    def test_filter_companies(self):
        """Test company filtering"""
        from src.processors.classifier import CompanyClassifier
        
        classifier = CompanyClassifier()
        
        companies = [
            {"company_code": "1111", "market": "تاسي", "shariah_board": "الراجحي"},
            {"company_code": "2222", "market": "نمو", "shariah_board": "المقاصد"},
            {"company_code": "3333", "market": "تاسي", "shariah_board": "الراجحي"},
        ]
        
        # Filter by market
        filtered = classifier.filter_companies(companies, market="تاسي")
        assert len(filtered) == 2
        
        # Filter by Shariah board
        filtered = classifier.filter_companies(companies, shariah_board="الراجحي")
        assert len(filtered) == 2
        
        # Filter by both
        filtered = classifier.filter_companies(
            companies, 
            market="تاسي", 
            shariah_board="الراجحي"
        )
        assert len(filtered) == 2

class TestExporters:
    """Test data exporters"""
    
    def test_json_export(self, tmp_path):
        """Test JSON export"""
        from src.exporters.json_exporter import JSONExporter
        
        exporter = JSONExporter(output_dir=tmp_path)
        
        companies = [
            {"company_code": "1111", "company_name": "Test 1"},
            {"company_code": "2222", "company_name": "Test 2"},
        ]
        
        filepath = exporter.export_flat(companies, "test.json")
        
        assert filepath.exists()
        assert filepath.suffix == ".json"
        
        # Read and verify content
        import json
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        assert len(data) == 2
        assert data[0]["company_code"] == "1111"
    
    def test_csv_export(self, tmp_path):
        """Test CSV export"""
        from src.exporters.csv_exporter import CSVExporter
        
        exporter = CSVExporter(output_dir=tmp_path)
        
        companies = [
            {"company_code": "1111", "company_name": "Test 1", "market": "تاسي"},
            {"company_code": "2222", "company_name": "Test 2", "market": "نمو"},
        ]
        
        filepath = exporter.export(companies, "test.csv")
        
        assert filepath.exists()
        assert filepath.suffix == ".csv"
        
        # Read and verify content
        import pandas as pd
        df = pd.read_csv(filepath)
        
        assert len(df) == 2
        assert df.iloc[0]["company_code"] == "1111"

# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])