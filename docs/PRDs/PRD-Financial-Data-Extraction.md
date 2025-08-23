# Product Requirements Document: Financial Data Extraction Pipeline

## 1. Project Overview

### Project Name
Al-Maqased Financial Analysis Data Extraction Pipeline

### Project Description
This project automates the extraction, processing, and transformation of financial data from PDF documents available on the Al-Maqased website. The system will download PDFs containing company financial results, extract tabular data, organize it by years, and provide the data in multiple formats for analysis.

### Business Context
The Al-Maqased website hosts financial analysis reports for companies in PDF format. These documents contain valuable financial data in tables that need to be extracted and made available in machine-readable formats for further analysis and research.

## 2. Objectives

### Primary Objectives
1. Automate the download of all PDF documents from the specified URL
2. Extract all financial tables from the downloaded PDFs
3. Organize and structure the data by company and year
4. Provide the data in multiple standard formats
5. Create a well-documented repository for the extracted data

### Secondary Objectives
1. Ensure data integrity and accuracy during extraction
2. Handle various table formats and structures
3. Provide clear documentation for future maintenance
4. Enable easy updates when new PDFs are added

## 3. Scope

### In Scope
- Web scraping the specified URL for PDF links
- Downloading all available PDF files
- Extracting tables containing company financial results
- Data cleaning and normalization
- Grouping data by years
- Converting data to JSON, XML, CSV, XLSX formats
- Creating comprehensive documentation
- Setting up a Git repository with proper structure

### Out of Scope
- Analysis of the financial data
- Creating visualization dashboards
- Real-time monitoring of new PDFs
- Translation of Arabic content
- Data validation against external sources

## 4. Technical Requirements

### Programming Language
- Python 3.8+ (recommended for PDF processing capabilities)

### Required Libraries
- **Web Scraping**: `requests`, `beautifulsoup4`, `selenium` (if needed)
- **PDF Processing**: `PyPDF2`, `pdfplumber`, `tabula-py`, `camelot-py`
- **Data Processing**: `pandas`, `numpy`
- **File Format Conversion**: `openpyxl`, `xlsxwriter`, `json`, `xml.etree.ElementTree`
- **Progress Tracking**: `tqdm`
- **Logging**: `logging`

### System Requirements
- Minimum 8GB RAM (for processing large PDFs)
- 10GB+ free disk space
- Stable internet connection
- Git installed

## 5. Functional Requirements

### 5.1 Web Scraping Module
**Purpose**: Discover and download all PDF files from the target URL

**Requirements**:
- Navigate to the specified URL
- Parse the HTML to find all PDF links
- Handle pagination if present
- Implement retry logic for failed downloads
- Track download progress
- Save PDFs with meaningful names (include company name and date if available)

**Error Handling**:
- Network timeouts
- 404 errors
- Partial downloads
- Rate limiting

### 5.2 PDF Processing Module
**Purpose**: Extract tabular data from PDF files

**Requirements**:
- Support multiple table extraction methods (fallback strategies)
- Handle Arabic text encoding properly
- Preserve table structure and relationships
- Extract metadata (company name, report date, etc.)
- Handle multi-page tables
- Deal with various table formats and layouts

**Challenges to Address**:
- Scanned PDFs vs. text-based PDFs
- Complex table layouts
- Merged cells
- Arabic RTL text handling

### 5.3 Data Processing Module
**Purpose**: Clean, normalize, and structure extracted data

**Requirements**:
- Data validation and cleaning
- Standardize column names
- Handle missing values appropriately
- Convert data types (strings to numbers, dates, etc.)
- Group data by years
- Merge data from multiple sources if needed
- Create a master dataset with all companies

**Data Structure**:
```json
{
  "company_name": "string",
  "year": "integer",
  "financial_data": {
    "revenue": "number",
    "expenses": "number",
    "net_profit": "number",
    // ... other financial metrics
  },
  "metadata": {
    "source_file": "string",
    "extraction_date": "datetime",
    "report_type": "string"
  }
}
```

### 5.4 Format Conversion Module
**Purpose**: Export data in multiple formats

**Requirements**:
- JSON: Nested structure preserving relationships
- CSV: Flat structure with proper headers
- XLSX: Multiple sheets (one per year or company)
- XML: Well-formed with proper schema

**Output Structure**:
```
output/
├── json/
│   ├── all_companies.json
│   ├── by_year/
│   │   ├── 2020.json
│   │   ├── 2021.json
│   │   └── ...
│   └── by_company/
│       ├── company_a.json
│       └── ...
├── csv/
│   ├── all_companies.csv
│   └── by_year/
│       └── ...
├── xlsx/
│   └── financial_data.xlsx
└── xml/
    └── financial_data.xml
```

### 5.5 Documentation Module
**Purpose**: Create comprehensive documentation

**Requirements**:
- README.md with project overview
- Installation instructions
- Usage guide
- Data dictionary
- API documentation (if applicable)
- Examples of data usage
- Troubleshooting guide

## 6. Data Processing Pipeline

### Pipeline Stages
1. **Discovery Stage**
   - Scrape website for PDF URLs
   - Create download queue
   
2. **Download Stage**
   - Download PDFs with progress tracking
   - Verify file integrity
   - Store in organized directory structure

3. **Extraction Stage**
   - Process each PDF
   - Extract tables
   - Extract metadata
   - Save raw extracted data

4. **Transformation Stage**
   - Clean and normalize data
   - Validate data quality
   - Group by years
   - Create relationships

5. **Export Stage**
   - Generate all format versions
   - Create summary statistics
   - Generate documentation

6. **Repository Stage**
   - Initialize Git repository
   - Create proper directory structure
   - Commit all files
   - Push to remote repository

## 7. Directory Structure

```
financial-data-extraction/
├── README.md
├── requirements.txt
├── .gitignore
├── src/
│   ├── __init__.py
│   ├── scraper.py
│   ├── pdf_extractor.py
│   ├── data_processor.py
│   ├── format_converter.py
│   └── utils/
│       ├── __init__.py
│       ├── logging_config.py
│       └── helpers.py
├── data/
│   ├── raw_pdfs/
│   ├── extracted_tables/
│   └── processed/
├── output/
│   ├── json/
│   ├── csv/
│   ├── xlsx/
│   └── xml/
├── logs/
│   └── extraction.log
├── tests/
│   ├── test_scraper.py
│   ├── test_extractor.py
│   └── test_processor.py
└── docs/
    ├── data_dictionary.md
    ├── usage_guide.md
    └── troubleshooting.md
```

## 8. Quality Assurance

### Data Quality Checks
- Completeness: All expected fields present
- Accuracy: Numeric values within reasonable ranges
- Consistency: Same company names across years
- Uniqueness: No duplicate entries
- Timeliness: Data extraction date recorded

### Testing Requirements
- Unit tests for each module
- Integration tests for pipeline
- Sample data for testing
- Validation against manually extracted samples

## 9. Performance Requirements

- Process a 50-page PDF in under 2 minutes
- Handle PDFs up to 500 pages
- Support parallel processing for multiple PDFs
- Memory usage not to exceed 4GB per PDF

## 10. Error Handling and Logging

### Logging Levels
- INFO: Progress updates, successful operations
- WARNING: Recoverable issues, data quality concerns
- ERROR: Failed operations, missing data
- DEBUG: Detailed processing information

### Error Recovery
- Automatic retry for network failures
- Fallback extraction methods
- Partial data recovery
- Clear error reporting

## 11. Success Criteria

1. Successfully download 100% of available PDFs
2. Extract tables from at least 95% of PDFs
3. Achieve 98%+ accuracy in data extraction (validated against samples)
4. Generate all required output formats
5. Complete documentation available
6. Repository successfully created and pushed
7. Process completes within 4 hours for initial run

## 12. Future Enhancements

1. Automated scheduling for periodic updates
2. Web interface for data browsing
3. API endpoint for data access
4. Data visualization dashboard
5. Machine learning for improved table detection
6. Support for additional document formats

## 13. Assumptions and Constraints

### Assumptions
- PDFs contain structured tables (not just images)
- Internet connection remains stable during download
- PDF format remains consistent
- Arabic text can be extracted properly

### Constraints
- Processing time limited by PDF complexity
- Memory constraints for very large PDFs
- Accuracy dependent on PDF quality
- Manual review may be needed for complex tables

## 14. Deliverables

1. **Source Code**: Complete Python application with all modules
2. **Extracted Data**: All formats (JSON, CSV, XLSX, XML)
3. **Documentation**: README, usage guide, data dictionary
4. **Repository**: Git repository with proper structure
5. **Logs**: Extraction logs and error reports
6. **Test Results**: Unit test results and validation reports

## 15. Implementation Timeline

### Phase 1: Setup and Scraping (Day 1)
- Environment setup
- Web scraping implementation
- PDF download functionality

### Phase 2: Extraction (Day 2-3)
- PDF processing implementation
- Table extraction
- Data validation

### Phase 3: Processing (Day 4)
- Data cleaning
- Grouping by years
- Format conversion

### Phase 4: Documentation and Deployment (Day 5)
- Documentation writing
- Repository setup
- Final testing and deployment

---

## Appendix A: Sample Code Structure

### Main Pipeline Script
```python
# main.py
import logging
from src.scraper import PDFScraper
from src.pdf_extractor import PDFExtractor
from src.data_processor import DataProcessor
from src.format_converter import FormatConverter

def main():
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize components
    scraper = PDFScraper()
    extractor = PDFExtractor()
    processor = DataProcessor()
    converter = FormatConverter()
    
    # Run pipeline
    pdf_urls = scraper.discover_pdfs()
    scraper.download_pdfs(pdf_urls)
    
    raw_data = extractor.extract_all_tables()
    processed_data = processor.process_data(raw_data)
    
    converter.export_all_formats(processed_data)
    
if __name__ == "__main__":
    main()
```

## Appendix B: Data Dictionary

| Field Name | Type | Description | Example |
|------------|------|-------------|---------|
| company_name | string | Name of the company | "شركة الأسمنت العربية" |
| year | integer | Financial year | 2023 |
| revenue | decimal | Total revenue in currency | 1500000.00 |
| net_profit | decimal | Net profit after tax | 250000.00 |
| assets | decimal | Total assets | 5000000.00 |
| liabilities | decimal | Total liabilities | 3000000.00 |
| source_file | string | Original PDF filename | "annual_report_2023.pdf" |
| extraction_date | datetime | When data was extracted | "2024-01-15T10:30:00" |
